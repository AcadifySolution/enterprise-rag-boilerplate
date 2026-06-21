import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.parsers.hierarchical_parser import HierarchicalParser
from app.services.chunkers.semantic_chunker import SemanticChunker

client = TestClient(app)

def test_hierarchical_parser():
    """
    Asserts correct hierarchical node extraction and parent-child parent_id assignment.
    """
    markdown_doc = """# Header One
Intro content.
## Header One Point One
Subset content.
# Header Two
Separated root content.
"""
    nodes = HierarchicalParser.parse_markdown(markdown_doc, "test_doc.md")
    assert len(nodes) >= 3
    
    node_h1 = next(n for n in nodes if "Header One" in n["text"] and "Point One" not in n["text"])
    node_h1_1 = next(n for n in nodes if "Header One Point One" in n["text"])
    node_h2 = next(n for n in nodes if "Header Two" in n["text"])
    
    assert node_h1["metadata"]["parent_id"] is None
    assert node_h1_1["metadata"]["parent_id"] == node_h1["id"]
    assert node_h2["metadata"]["parent_id"] is None

def test_semantic_chunker():
    """
    Asserts text is correctly partitioned into token chunks containing proper metadata tags.
    """
    node = {
        "id": "parent-node-xyz",
        "text": "This is sentence one. Here comes sentence two. Let's append sentence three.",
        "metadata": {"source": "test.md"}
    }
    # Force low size to trigger multi-chunk outputs
    chunker = SemanticChunker(chunk_size=12, chunk_overlap=3)
    chunks = chunker.chunk_node(node)
    
    assert len(chunks) > 0
    for idx, chunk in enumerate(chunks):
        assert chunk["id"] == f"parent-node-xyz_chunk_{idx}"
        assert chunk["metadata"]["parent_chunk_id"] == "parent-node-xyz"
        assert "chunk_index" in chunk["metadata"]
        assert "token_count" in chunk["metadata"]

def test_ingest_text_endpoint():
    """
    Verifies that the raw text ingestion POST endpoint functions.
    """
    payload = {
        "text": "# Acadify Engineering Standards\n1. Maintain zero-trust PII masking.",
        "source_name": "engineering_standards.md"
    }
    response = client.post("/api/ingestion/text", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert data["processed_chunks"] > 0

def test_ingest_file_endpoint():
    """
    Verifies file upload multipart ingestion parses files and returns successfully.
    """
    file_payload = {
        "file": ("systems_architecture.md", b"# Systems Info\nHigh availability is configured.", "text/markdown")
    }
    response = client.post("/api/ingestion/file", files=file_payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert data["processed_chunks"] > 0
