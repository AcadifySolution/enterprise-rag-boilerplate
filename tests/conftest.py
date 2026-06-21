import pytest
import numpy as np
from typing import List, Dict, Any, Optional
from app.services.vector_stores.base import BaseVectorStore
from app.services.vector_stores import factory

class InMemoryVectorStore(BaseVectorStore):
    """
    An in-memory implementation of BaseVectorStore for self-contained unit testing.
    Estimates actual cosine similarity using numpy dot products.
    """
    def __init__(self):
        self.storage = {} # id -> (vector, metadata, text)

    async def upsert(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]],
        texts: List[str]
    ) -> bool:
        for idx, vec, meta, txt in zip(ids, vectors, metadatas, texts):
            self.storage[idx] = (vec, meta, txt)
        return True

    async def query(
        self,
        vector: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        results = []
        vec_np = np.array(vector)
        
        for idx, (stored_vec, meta, txt) in self.storage.items():
            # Check filter parameters
            match = True
            if filter_dict:
                for key, val in filter_dict.items():
                    if meta.get(key) != val:
                        match = False
                        break
            if not match:
                continue
            
            # Dot product similarity (assuming unit normalization)
            stored_np = np.array(stored_vec)
            dot = np.dot(vec_np, stored_np)
            norm_q = np.linalg.norm(vec_np)
            norm_s = np.linalg.norm(stored_np)
            
            similarity = float(dot / (norm_q * norm_s)) if (norm_q > 0 and norm_s > 0) else 0.0
            
            results.append({
                "id": idx,
                "score": similarity,
                "text": txt,
                "metadata": meta
            })
            
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    async def delete(self, ids: List[str]) -> bool:
        for idx in ids:
            self.storage.pop(idx, None)
        return True

    async def clear(self) -> bool:
        self.storage.clear()
        return True

    async def verify_connectivity(self) -> bool:
        return True

@pytest.fixture(autouse=True)
def mock_vector_store(monkeypatch):
    """
    Overrides the get_vector_store factory globally during tests in all importing modules.
    """
    store = InMemoryVectorStore()
    
    from app.services.ingestor import async_ingestor
    from app.services.retriever import multi_stage_retriever
    from app.api import health_router
    
    monkeypatch.setattr(async_ingestor, "get_vector_store", lambda: store)
    monkeypatch.setattr(multi_stage_retriever, "get_vector_store", lambda: store)
    monkeypatch.setattr(health_router, "get_vector_store", lambda: store)
    monkeypatch.setattr(factory, "get_vector_store", lambda: store)
    return store
