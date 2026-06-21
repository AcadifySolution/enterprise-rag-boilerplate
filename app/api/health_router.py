from fastapi import APIRouter
from app.services.vector_stores.factory import get_vector_store
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
async def health_check():
    """
    Performs live auditing checks on vector databases and internal services.
    """
    try:
        vector_store = get_vector_store()
        db_connected = await vector_store.verify_connectivity()
    except Exception:
        db_connected = False

    return {
        "status": "healthy" if db_connected else "degraded",
        "vector_db_type": settings.VECTOR_DB_TYPE,
        "vector_db_connected": db_connected,
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV
    }
