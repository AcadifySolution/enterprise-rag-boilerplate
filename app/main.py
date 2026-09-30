from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health_router import router as health_router
from app.api.ingestion_router import router as ingestion_router
from app.api.query_router import router as query_router
from app.core.config import settings
from app.core.logging import logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.APP_ENV)
    logger.info("Booting %s under environment: %s", settings.APP_NAME, settings.APP_ENV)

    if settings.VECTOR_DB_TYPE.lower() == "pgvector":
        try:
            from app.services.vector_stores.pgvector import PgVectorStore

            store = PgVectorStore()
            await store._init_db()
        except Exception:
            logger.exception("Failed to initialize PostgreSQL pgvector schema")

    yield
    logger.info("Terminating API service process.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise reference RAG backend with configurable retrieval and vector-store adapters.",
    version="0.1.0",
    lifespan=lifespan,
)

allowed_origins = [
    origin.strip()
    for origin in settings.CORS_ALLOWED_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)

app.include_router(ingestion_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(health_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Enterprise RAG Reference API.",
        "documentation": "/docs",
    }
