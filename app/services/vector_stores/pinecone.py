import asyncio
from typing import List, Dict, Any, Optional
from pinecone import Pinecone as PineconeClient
from app.core.config import settings
from app.services.vector_stores.base import BaseVectorStore
from app.core.logging import logger

class PineconeVectorStore(BaseVectorStore):
    """
    Pinecone client wrapper implementing BaseVectorStore.
    """
    def __init__(self):
        # We allow initial initialization without error for test frameworks/mocks
        api_key = settings.PINECONE_API_KEY or "mock-api-key"
        index_name = settings.PINECONE_INDEX_NAME or "mock-index"
        self.pc = PineconeClient(api_key=api_key)
        self.index_name = index_name
        self._index = None

    @property
    def index(self):
        if self._index is None:
            self._index = self.pc.Index(self.index_name)
        return self._index

    async def upsert(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]],
        texts: List[str]
    ) -> bool:
        try:
            records = []
            for idx, vec, meta, txt in zip(ids, vectors, metadatas, texts):
                pinecone_meta = {**meta, "text": txt}
                records.append((idx, vec, pinecone_meta))
            
            # Execute upsert in executor thread
            await asyncio.to_thread(self.index.upsert, vectors=records)
            return True
        except Exception as e:
            logger.error(f"Pinecone upsert failed: {str(e)}")
            return False

    async def query(
        self,
        vector: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        try:
            # Query in thread
            res = await asyncio.to_thread(
                self.index.query,
                vector=vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            results = []
            for match in res.matches:
                meta = match.metadata or {}
                text = meta.pop("text", "")
                results.append({
                    "id": match.id,
                    "score": match.score,
                    "text": text,
                    "metadata": meta
                })
            return results
        except Exception as e:
            logger.error(f"Pinecone query failed: {str(e)}")
            return []

    async def delete(self, ids: List[str]) -> bool:
        try:
            await asyncio.to_thread(self.index.delete, ids=ids)
            return True
        except Exception as e:
            logger.error(f"Pinecone delete failed: {str(e)}")
            return False

    async def clear(self) -> bool:
        try:
            await asyncio.to_thread(self.index.delete, delete_all=True)
            return True
        except Exception as e:
            logger.error(f"Pinecone clear failed: {str(e)}")
            return False

    async def verify_connectivity(self) -> bool:
        try:
            await asyncio.to_thread(self.pc.list_indexes)
            return True
        except Exception as e:
            logger.error(f"Pinecone connection verification failed: {str(e)}")
            return False
