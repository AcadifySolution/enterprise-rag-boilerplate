import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Enterprise RAG Boilerplate"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    API_KEY: str = "dev-api-key-secure-12345"

    # LLM Provider Keys
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    # Vector Database configuration: pgvector, qdrant, pinecone
    VECTOR_DB_TYPE: str = "qdrant"

    # pgvector configuration
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/rag_db"

    # Qdrant configuration
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "rag_documents"

    # Pinecone configuration
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_INDEX_NAME: str = "rag-index"

    # Ingestion & Chunking parameters
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # Compliance Config
    PII_MASKING_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
