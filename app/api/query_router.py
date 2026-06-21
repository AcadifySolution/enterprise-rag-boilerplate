from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import RAGService
from app.core.logging import logger

router = APIRouter(prefix="/query", tags=["query"])

@router.post("", response_model=QueryResponse)
async def query_rag(payload: QueryRequest):
    """
    Executes the full retrieval-augmented generation sequence:
    PII masking, multi-stage retrieval, LLM response rendering, and groundedness verifications.
    """
    try:
        rag_service = RAGService()
        response = await rag_service.answer_query(
            query=payload.query,
            filter_dict=payload.filter_dict,
            top_k=payload.top_k
        )
        return response
    except Exception as e:
        logger.error(f"Query API endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
