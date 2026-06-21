import asyncio
from typing import List, Dict, Any
from app.services.parsers.hierarchical_parser import HierarchicalParser
from app.services.chunkers.semantic_chunker import SemanticChunker
from app.services.embeddings import EmbeddingsService
from app.services.vector_stores.factory import get_vector_store
from app.core.pii_masking import PIIMasker
from app.core.logging import logger

class AsyncIngestor:
    """
    Manages end-to-end parallel document parsing, chunking, and database ingestion.
    """
    def __init__(self, batch_size: int = 16, max_concurrency: int = 4):
        self.chunker = SemanticChunker()
        self.embeddings_service = EmbeddingsService()
        self.vector_store = get_vector_store()
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def ingest_document(self, text: str, source_name: str) -> Dict[str, Any]:
        """
        Executes ingestion. Sanitizes text using PII masking, structures hierarchy,
        calculates embeddings in parallel, and uploads records to active vector store.
        """
        logger.info(f"Initiating ingestion chain for: {source_name}")
        
        # 1. Hierarchical markdown parser
        nodes = HierarchicalParser.parse_markdown(text, source_name)
        logger.info(f"Hierarchical parser produced {len(nodes)} sections.")
        
        # 2. Apply PII sanitization and sub-chunk mapping
        chunks = []
        for node in nodes:
            # Mask PII in both text and header metadata to prevent database exposure
            node["text"] = PIIMasker.mask_text(node["text"])
            node["metadata"]["heading_title"] = PIIMasker.mask_text(node["metadata"]["heading_title"])
            
            sub_chunks = self.chunker.chunk_node(node)
            chunks.extend(sub_chunks)
            
        logger.info(f"Chunker partitioned sections into {len(chunks)} total sub-chunks.")
        
        if not chunks:
            return {"status": "success", "processed_chunks": 0}

        # 3. Create throttled parallel task batches
        tasks = []
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i : i + self.batch_size]
            tasks.append(self._process_batch(batch))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        failures = sum(1 for res in results if isinstance(res, Exception) or res is False)
        if failures > 0:
            logger.error(f"Ingestion finished with {failures} batch upload errors.")
            return {
                "status": "partial_success", 
                "processed_chunks": max(0, len(chunks) - (failures * self.batch_size))
            }
            
        logger.info("Successfully ingested all documents without errors.")
        return {"status": "success", "processed_chunks": len(chunks)}

    async def _process_batch(self, batch: List[Dict[str, Any]]) -> bool:
        """
        Processes and upserts a single batch under semaphore throttling.
        """
        async with self.semaphore:
            try:
                ids = [item["id"] for item in batch]
                texts = [item["text"] for item in batch]
                metadatas = [item["metadata"] for item in batch]
                
                # Fetch embeddings (using cached/mock/langchain calls)
                vectors = await self.embeddings_service.embed_texts(texts)
                
                # Store in target database
                success = await self.vector_store.upsert(
                    ids=ids,
                    vectors=vectors,
                    metadatas=metadatas,
                    texts=texts
                )
                return success
            except Exception as e:
                logger.error(f"Batch processing failed: {str(e)}")
                return False
