import pytest

from app.services.retriever.multi_stage_retriever import MultiStageRetriever


@pytest.mark.asyncio
async def test_expansion_keeps_original_scope(mock_vector_store):
    shared_parent = "shared-parent"
    await mock_vector_store.upsert(
        ids=["allowed", "other-tenant", "draft"],
        vectors=[[1.0] * 1536] * 3,
        metadatas=[
            {"tenant": "a", "status": "published", "parent_chunk_id": shared_parent},
            {"tenant": "b", "status": "published", "parent_chunk_id": shared_parent},
            {"tenant": "a", "status": "draft", "parent_chunk_id": shared_parent},
        ],
        texts=["Allowed content", "Other tenant secret", "Unpublished content"],
    )
    retriever = MultiStageRetriever()
    scope = {"tenant": "a", "status": "published"}
    results = await retriever.retrieve("content", top_k=5, filter_dict=scope)
    assert [row["id"] for row in results] == ["allowed"]
    assert scope == {"tenant": "a", "status": "published"}


@pytest.mark.asyncio
async def test_expansion_retains_parent_filter(mock_vector_store):
    await mock_vector_store.upsert(
        ids=["allowed", "other-parent"],
        vectors=[[1.0] * 1536] * 2,
        metadatas=[{"parent_chunk_id": "a"}, {"parent_chunk_id": "b"}],
        texts=["Allowed content", "Other content"],
    )
    results = await MultiStageRetriever().retrieve(
        "content", top_k=5, filter_dict={"parent_chunk_id": "a"}
    )
    assert [row["id"] for row in results] == ["allowed"]
