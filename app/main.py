from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.api.ingestion_router import router as ingestion_router
from app.api.query_router import router as query_router
from app.api.health_router import router as health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages API service lifecycle tasks.
    """
    # 1. Setup structured logging
    setup_logging(settings.APP_ENV)
    logger.info(f"Booting {settings.APP_NAME} under environment: {settings.APP_ENV}")
    
    # 2. Trigger automatic DB migrations for pgvector if configured
    if settings.VECTOR_DB_TYPE.lower() == "pgvector":
        try:
            from app.services.vector_stores.pgvector import PgVectorStore
            store = PgVectorStore()
            await store._init_db()
        except Exception as e:
            logger.error(f"Failed to auto-migrate PostgreSQL pgvector schema: {str(e)}")
            
    yield
    logger.info("Terminating API service process.")

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Reference RAG Backend Boilerplate.",
    version="0.1.0",
    lifespan=lifespan
)

# Register CORS policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect endpoints
app.include_router(ingestion_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(health_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Enterprise RAG Reference API.",
        "documentation": "/docs"
    }
