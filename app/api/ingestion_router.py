from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.models.schemas import IngestTextRequest, IngestResponse
from app.services.ingestor.async_ingestor import AsyncIngestor
from app.core.logging import logger

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

@router.post("/text", response_model=IngestResponse)
async def ingest_text(payload: IngestTextRequest):
    """
    Ingests text block contents, processing them through hierarchical parsing,
    semantic chunking, PII scrubbing, and vector storage.
    """
    try:
        ingestor = AsyncIngestor()
        result = await ingestor.ingest_document(payload.text, payload.source_name)
        return result
    except Exception as e:
        logger.error(f"Text ingestion endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/file", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...)):
    """
    Accepts text or Markdown file uploads, extracts contents, and routes to ingestion.
    """
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        
        ingestor = AsyncIngestor()
        result = await ingestor.ingest_document(text_content, file.filename)
        return result
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded plain text/markdown.")
    except Exception as e:
        logger.error(f"File ingestion endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
