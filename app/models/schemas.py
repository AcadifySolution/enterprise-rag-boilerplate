from typing import Any

from pydantic import BaseModel, Field, field_validator


class IngestTextRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2_000_000)
    source_name: str = Field(..., min_length=1, max_length=512)


class IngestResponse(BaseModel):
    status: str = Field(...)
    processed_chunks: int = Field(..., ge=0)


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10_000)
    top_k: int = Field(default=3, ge=1, le=20)
    filter_dict: dict[str, Any] | None = Field(default=None)

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str) -> str:
        return value.strip()


class ContextChunkModel(BaseModel):
    id: str
    score: float
    text: str
    metadata: dict[str, Any]


class CitationModel(BaseModel):
    sentence: str
    source_chunk_id: str | None
    source_file: str | None
    overlap_score: float
    is_grounded: bool


class VerificationModel(BaseModel):
    groundedness_score: float
    is_hallucinated: bool
    citations: list[CitationModel]


class QueryResponse(BaseModel):
    query: str
    answer: str
    contexts: list[ContextChunkModel]
    verification: VerificationModel
