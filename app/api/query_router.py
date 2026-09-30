from fastapi import APIRouter, Depends, HTTPException

from app.core.logging import logger
from app.core.security import require_api_key
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import RAGService

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse, dependencies=[Depends(require_api_key)])
async def query_rag(payload: QueryRequest):
    """Execute retrieval, generation, and groundedness verification."""
    try:
        rag_service = RAGService()
        return await rag_service.answer_query(
            query=payload.query,
            filter_dict=payload.filter_dict,
            top_k=payload.top_k,
        )
    except Exception:
        logger.exception("Query API endpoint error")
        raise HTTPException(status_code=500, detail="Internal server error")
