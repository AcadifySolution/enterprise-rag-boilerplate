import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ingestor.async_ingestor import AsyncIngestor
from app.services.retriever.multi_stage_retriever import MultiStageRetriever
from app.services.verifier.verifier import ResponseVerifier

client = TestClient(app)

@pytest.mark.asyncio
async def test_retrieval_and_expansion():
    """
    Validates that retrieving search context returns candidate results with siblings.
    """
    ingestor = AsyncIngestor()
    doc_text = """# Standard Protocol
The pipeline enforces rigid compliance protocols.
## Sub Protocol
Security logging operates 24/7.
"""
    await ingestor.ingest_document(doc_text, "protocol.md")
    
    retriever = MultiStageRetriever()
    results = await retriever.retrieve(query="compliance protocols", top_k=2)
    
    assert len(results) > 0
    # Verifies retrieval returned text matching query keywords
    assert any("compliance protocols" in r["text"] or "Security logging" in r["text"] for r in results)

def test_response_verifier():
    """
    Checks that groundedness scores and citations match context sources.
    """
    contexts = [
        {"id": "doc-a_chunk_0", "text": "Acadify is a distributed engineering partner.", "metadata": {"source": "standard.md"}},
        {"id": "doc-b_chunk_0", "text": "We build secure cloud architectures.", "metadata": {"source": "cloud.md"}}
    ]
    
    # 1. 100% grounded response
    response_g = "Acadify is a distributed engineering partner. We build secure cloud architectures."
    res_g = ResponseVerifier.verify(response_g, contexts)
    
    assert res_g["groundedness_score"] == 1.0
    assert res_g["is_hallucinated"] is False
    assert len(res_g["citations"]) == 2
    assert res_g["citations"][0]["source_chunk_id"] == "doc-a_chunk_0"
    assert res_g["citations"][1]["source_chunk_id"] == "doc-b_chunk_0"
    
    # 2. Hallucinated response
    response_h = "Acadify is an engineering partner. They operate rocket ships to outer space."
    res_h = ResponseVerifier.verify(response_h, contexts)
    
    assert res_h["groundedness_score"] < 1.0
    assert res_h["citations"][1]["is_grounded"] is False
    assert res_h["citations"][1]["source_chunk_id"] is None

def test_query_rag_endpoint():
    """
    Validates end-to-end FastAPI query RAG router execution flow.
    """
    # Pre-populate some document text
    client.post(
        "/api/ingestion/text",
        json={
            "text": "# Operations Guide\nOur developers deploy secure Kubernetes foundations.",
            "source_name": "operations.md"
        }
    )
    
    query_payload = {"query": "What do developers deploy?", "top_k": 2}
    response = client.post("/api/query", json=query_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["query"] == "What do developers deploy?"
    assert "deploy" in data["answer"].lower()
    assert len(data["contexts"]) > 0
    assert "verification" in data

def test_health_endpoint():
    """
    Asserts readiness status checks return healthy.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert data["vector_db_connected"] is True
