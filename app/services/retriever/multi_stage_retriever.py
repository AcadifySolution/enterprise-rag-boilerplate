import re
import asyncio
from typing import List, Dict, Any, Optional
from app.services.vector_stores.base import BaseVectorStore
from app.services.vector_stores.factory import get_vector_store
from app.services.embeddings import EmbeddingsService
from app.core.logging import logger

class MultiStageRetriever:
    """
    Implements a multi-stage context retrieval chain.
    """
    def __init__(self):
        self.vector_store = get_vector_store()
        self.embeddings_service = EmbeddingsService()

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        enable_expansion: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Orchestrates retrieval pipeline:
        Stage 1: Semantic query search.
        Stage 2: Context expansion to fetch sibling document segments.
        Stage 3: Term-frequency/keyword overlap reranking.
        """
        logger.info(f"Initiating search context retrieval for query: '{query}'")
        
        # Stage 1: Generate query embedding and fetch matches
        query_vector = await self.embeddings_service.embed_query(query)
        candidates = await self.vector_store.query(
            vector=query_vector,
            top_k=top_k,
            filter_dict=filter_dict
        )
        
        if not candidates:
            logger.info("Vector DB query returned 0 matches.")
            return []
            
        logger.info(f"Retrieved {len(candidates)} raw matches from database.")

        # Stage 2: Sibling context expansion
        final_candidates = []
        seen_ids = set()

        if enable_expansion:
            for cand in candidates:
                parent_chunk_id = cand["metadata"].get("parent_chunk_id")
                if parent_chunk_id:
                    # Query for siblings that share the same hierarchical parent node
                    siblings = await self.vector_store.query(
                        vector=query_vector,
                        top_k=10,
                        filter_dict={"parent_chunk_id": parent_chunk_id}
                    )
                    for sib in siblings:
                        if sib["id"] not in seen_ids:
                            seen_ids.add(sib["id"])
                            final_candidates.append(sib)
                else:
                    if cand["id"] not in seen_ids:
                        seen_ids.add(cand["id"])
                        final_candidates.append(cand)
        else:
            final_candidates = candidates

        # Stage 3: Keyword/Term overlap Reranking
        query_terms = set(re.findall(r'\w+', query.lower()))
        for cand in final_candidates:
            cand_terms = set(re.findall(r'\w+', cand["text"].lower()))
            overlap_count = len(query_terms.intersection(cand_terms))
            # Boost score based on keyword overlap
            cand["rerank_score"] = cand["score"] + (0.05 * overlap_count)
            
        # Re-sort descending based on the computed rerank score
        final_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        # Truncate to top_k requested
        results = final_candidates[:top_k]
        logger.info(f"Multi-stage retrieval finalized. Returning {len(results)} contexts.")
        return results
