import asyncio
from typing import List, Dict, Any, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from app.core.config import settings
from app.services.vector_stores.base import BaseVectorStore
from app.core.logging import logger

class QdrantVectorStore(BaseVectorStore):
    """
    Qdrant client wrapper implementing BaseVectorStore.
    """
    def __init__(self):
        url = settings.QDRANT_URL or "http://localhost:6333"
        api_key = settings.QDRANT_API_KEY
        self.client = AsyncQdrantClient(url=url, api_key=api_key)
        self.collection_name = settings.QDRANT_COLLECTION_NAME or "rag_documents"

    async def _ensure_collection(self, vector_size: int):
        try:
            exists = await self.client.collection_exists(self.collection_name)
            if not exists:
                logger.info(f"Creating Qdrant collection: {self.collection_name} with dimension: {vector_size}")
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE
                    )
                )
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {str(e)}")

    async def upsert(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]],
        texts: List[str]
    ) -> bool:
        if not vectors:
            return True
        try:
            await self._ensure_collection(len(vectors[0]))
            
            points = []
            for idx, vec, meta, txt in zip(ids, vectors, metadatas, texts):
                # Put payload text and other properties together
                payload = {**meta, "text": txt}
                points.append(
                    models.PointStruct(
                        id=idx,
                        vector=vec,
                        payload=payload
                    )
                )
            
            await self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            return True
        except Exception as e:
            logger.error(f"Qdrant upsert failed: {str(e)}")
            return False

    async def query(
        self,
        vector: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        try:
            exists = await self.client.collection_exists(self.collection_name)
            if not exists:
                return []
                
            qdrant_filter = None
            if filter_dict:
                must_filters = []
                for key, val in filter_dict.items():
                    must_filters.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=val)
                        )
                    )
                qdrant_filter = models.Filter(must=must_filters)

            hits = await self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=top_k,
                query_filter=qdrant_filter
            )

            results = []
            for hit in hits:
                payload = hit.payload or {}
                text = payload.pop("text", "")
                results.append({
                    "id": str(hit.id),
                    "score": hit.score,
                    "text": text,
                    "metadata": payload
                })
            return results
        except Exception as e:
            logger.error(f"Qdrant query failed: {str(e)}")
            return []

    async def delete(self, ids: List[str]) -> bool:
        try:
            # Check collection exists before deleting
            if not await self.client.collection_exists(self.collection_name):
                return True
                
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=ids)
            )
            return True
        except Exception as e:
            logger.error(f"Qdrant delete failed: {str(e)}")
            return False

    async def clear(self) -> bool:
        try:
            if await self.client.collection_exists(self.collection_name):
                await self.client.delete_collection(self.collection_name)
            return True
        except Exception as e:
            logger.error(f"Qdrant clear collection failed: {str(e)}")
            return False

    async def verify_connectivity(self) -> bool:
        try:
            await self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant connection verification failed: {str(e)}")
            return False
