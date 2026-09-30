from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.logging import logger
from app.core.security import require_api_key
from app.models.schemas import IngestResponse, IngestTextRequest
from app.services.ingestor.async_ingestor import AsyncIngestor

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/text", response_model=IngestResponse, dependencies=[Depends(require_api_key)])
async def ingest_text(payload: IngestTextRequest):
    """Ingest text through masking, parsing, chunking, embedding, and storage."""
    try:
        ingestor = AsyncIngestor()
        return await ingestor.ingest_document(payload.text, payload.source_name)
    except Exception:
        logger.exception("Text ingestion endpoint error")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/file", response_model=IngestResponse, dependencies=[Depends(require_api_key)])
async def ingest_file(file: UploadFile = File(...)):
    """Ingest a UTF-8 text/Markdown upload with a bounded payload size."""
    try:
        content = await file.read()
        if len(content) > 2_000_000:
            raise HTTPException(status_code=413, detail="File exceeds the 2 MB limit.")

        text_content = content.decode("utf-8")
        source_name = file.filename or "uploaded-document.txt"
        ingestor = AsyncIngestor()
        return await ingestor.ingest_document(text_content, source_name)
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded plain text or Markdown.",
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("File ingestion endpoint error")
        raise HTTPException(status_code=500, detail="Internal server error")
