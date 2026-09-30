from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Enterprise RAG Boilerplate"
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # API authentication. Required for staging/production.
    API_KEY: str = ""
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # LLM provider keys
    ANTHROPIC_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None

    # Vector database configuration
    VECTOR_DB_TYPE: str = "qdrant"

    # pgvector configuration
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/rag_db"

    # Qdrant configuration
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION_NAME: str = "rag_documents"

    # Pinecone configuration
    PINECONE_API_KEY: str | None = None
    PINECONE_INDEX_NAME: str = "rag-index"

    # Ingestion and chunking parameters
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Data protection
    PII_MASKING_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
