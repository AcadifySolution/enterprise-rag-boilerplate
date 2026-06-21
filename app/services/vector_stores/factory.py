from app.core.config import settings
from app.services.vector_stores.base import BaseVectorStore
from app.services.vector_stores.pinecone import PineconeVectorStore
from app.services.vector_stores.qdrant import QdrantVectorStore
from app.services.vector_stores.pgvector import PgVectorStore

def get_vector_store() -> BaseVectorStore:
    """
    Factory function instantiating the requested vector database wrapper.
    """
    db_type = settings.VECTOR_DB_TYPE.lower()
    if db_type == "pinecone":
        return PineconeVectorStore()
    elif db_type == "qdrant":
        return QdrantVectorStore()
    elif db_type == "pgvector":
        return PgVectorStore()
    else:
        raise ValueError(f"Unsupported vector database config: {settings.VECTOR_DB_TYPE}")
