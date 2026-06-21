from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class IngestTextRequest(BaseModel):
    text: str = Field(..., description="The document or text payload to ingest.", examples=["# System Standard\nOur service maintains 99.99% availability."])
    source_name: str = Field(..., description="Identifier name of the document source.", examples=["standards.md"])

class IngestResponse(BaseModel):
    status: str = Field(..., description="Result state of ingestion (e.g. success, partial_success).")
    processed_chunks: int = Field(..., description="The count of text sub-chunks successfully processed.")

class QueryRequest(BaseModel):
    query: str = Field(..., description="The query string to run through the RAG pipeline.")
    top_k: int = Field(default=3, description="Limit of context matches to retrieve.")
    filter_dict: Optional[Dict[str, Any]] = Field(default=None, description="Metadata key-value filters to narrow vector searches.")

class ContextChunkModel(BaseModel):
    id: str
    score: float
    text: str
    metadata: Dict[str, Any]

class CitationModel(BaseModel):
    sentence: str
    source_chunk_id: Optional[str]
    source_file: Optional[str]
    overlap_score: float
    is_grounded: bool

class VerificationModel(BaseModel):
    groundedness_score: float
    is_hallucinated: bool
    citations: List[CitationModel]

class QueryResponse(BaseModel):
    query: str
    answer: str
    contexts: List[ContextChunkModel]
    verification: VerificationModel
