import asyncio
import numpy as np
from typing import List
from app.core.config import settings
from app.core.logging import logger

class EmbeddingsService:
    """
    Orchestrates embedding generation using external APIs or local mock fallbacks.
    """
    def __init__(self):
        self.use_mock = True
        self.embeddings = None
        
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
            try:
                from langchain_openai import OpenAIEmbeddings
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=settings.OPENAI_API_KEY,
                    model=settings.EMBEDDING_MODEL
                )
                self.use_mock = False
                logger.info("OpenAI embeddings configured successfully.")
            except ImportError:
                logger.warning("langchain-openai package not installed. Falling back to mock embeddings.")

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of texts. Returns 1536-dimensional float arrays.
        """
        if self.use_mock or not self.embeddings:
            # Deterministic mock vectors generated from text hash values
            results = []
            for text_val in texts:
                seed = sum(ord(c) for c in text_val) % 100000
                rng = np.random.default_rng(seed)
                vector = rng.standard_normal(1536)
                # Normalize vector to unit length
                norm = np.linalg.norm(vector)
                if norm > 0:
                    vector = vector / norm
                results.append(vector.tolist())
            return results
        
        # Async invocation of langchain sync embeddings
        return await asyncio.to_thread(self.embeddings.embed_documents, texts)

    async def embed_query(self, query: str) -> List[float]:
        """
        Embeds a single query string.
        """
        vectors = await self.embed_texts([query])
        return vectors[0]
