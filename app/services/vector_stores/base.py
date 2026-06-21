from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseVectorStore(ABC):
    """
    Abstract interface defining unified actions for supported vector databases.
    """
    
    @abstractmethod
    async def upsert(
        self,
        ids: List[str],
        vectors: List[List[float]],
        metadatas: List[Dict[str, Any]],
        texts: List[str]
    ) -> bool:
        """
        Asynchronously batch-upserts embeddings, source texts, and associated metadata.
        """
        pass

    @abstractmethod
    async def query(
        self,
        vector: List[float],
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Queries vector space. Returns formatted candidate results:
        [
            {"id": str, "score": float, "text": str, "metadata": dict}
        ]
        """
        pass

    @abstractmethod
    async def delete(self, ids: List[str]) -> bool:
        """
        Deletes vector records by ID.
        """
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """
        Clears/drops the active index or collection.
        """
        pass

    @abstractmethod
    async def verify_connectivity(self) -> bool:
        """
        Verifies vector store connection status.
        """
        pass
