"""Unit and integration tests for the retrieval pipeline."""

import os
import shutil
import tempfile
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from app.schemas.document import Document
from app.loaders.markdown_loader import MarkdownLoader
from app.loaders.json_loader import JSONCaseLoader
from app.preprocessing.cleaner import TextCleaner
from app.preprocessing.chunker import DocumentChunker
from app.embeddings.embedding_model import LocalEmbeddingManager
from app.vectorstore.faiss_store import FAISSStoreManager
from app.retrieval.retriever import SemanticRetriever
from app.retrieval.ranking import SearchResultRanker


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Provides a temporary directory that is automatically cleaned up."""
    path = tempfile.mkdtemp()
    yield path
    shutil.rmtree(path)


def test_text_cleaner() -> None:
    """Test text cleaning, spacing collapses, and code block preservation."""
    cleaner = TextCleaner()

    # Whitespace and newline normalization
    raw_text = "Hello    World!\n\n\n\nNew Paragraph.\r\n"
    cleaned = cleaner.clean(raw_text)
    assert cleaned == "Hello World!\n\nNew Paragraph."

    # Code block protection
    code_text = "Some text.\n\n```python\nif x  ==  y:\n    print(  'hello'  )\n```\nMore text."
    cleaned_code = cleaner.clean(code_text)
    # The spaces inside the code block 'if x  ==  y:' and 'print(  "hello"  )' must be preserved!
    assert "if x  ==  y:" in cleaned_code
    assert "print(  'hello'  )" in cleaned_code
    # The normal text should have collapsed spacing
    assert "Some text.\n\n" in cleaned_code


def test_markdown_loader(temp_dir) -> None:
    """Test markdown loader parsing, header extraction, and encoding handling."""
    # Write a test markdown file
    md_path = os.path.join(temp_dir, "test_doc.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Hello H1 Title\nSome content description.\n\n- Bullet 1\n- Bullet 2")

    # Create empty file
    empty_path = os.path.join(temp_dir, "empty_doc.md")
    with open(empty_path, "w", encoding="utf-8") as f:
        f.write("")

    loader = MarkdownLoader(temp_dir)
    docs = loader.load()

    # The empty file should be skipped, so only 1 document is loaded
    assert len(docs) == 1
    assert docs[0].metadata["title"] == "Hello H1 Title"
    assert docs[0].metadata["filename"] == "test_doc.md"
    assert "Bullet 1" in docs[0].content


def test_json_loader(temp_dir) -> None:
    """Test loading and validating resolved case files."""
    json_path = os.path.join(temp_dir, "cases.json")
    valid_data = [
        {
            "case_id": "case_99",
            "category": "Testing",
            "question": "What is 2+2?",
            "answer": "It is equal to four.",
            "priority": 4,
            "metadata": {"source_env": "test"}
        }
    ]

    with open(json_path, "w", encoding="utf-8") as f:
        import json
        json.dump(valid_data, f)

    loader = JSONCaseLoader(json_path)
    docs = loader.load()

    assert len(docs) == 1
    assert docs[0].id == "case_99"
    assert docs[0].metadata["category"] == "Testing"
    assert docs[0].metadata["priority"] == 4
    assert docs[0].metadata["source_env"] == "test"


def test_document_chunker() -> None:
    """Test chunker split logic and metadata tags."""
    doc = Document(
        id="parent_doc",
        content="Line 1\n" * 150,  # Generates content long enough to trigger chunking
        metadata={"title": "Line Document", "filename": "lines.md"}
    )

    chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) > 1
    assert chunks[0].metadata["parent_id"] == "parent_doc"
    assert chunks[0].metadata["chunk_index"] == 0
    assert chunks[0].metadata["token_estimate"] > 0
    assert "filename" in chunks[0].metadata


def test_embedding_manager() -> None:
    """Test singleton and lazy instantiation of the embedding manager."""
    manager1 = LocalEmbeddingManager()
    manager2 = LocalEmbeddingManager()

    # Ensure singleton instance reference identity
    assert manager1 is manager2

    # Verify embeddings are loaded on demand and cache is shared
    emb1 = manager1.get_embeddings()
    emb2 = manager2.get_embeddings()
    assert emb1 is emb2


def test_faiss_persistence_and_deduplication(temp_dir) -> None:
    """Test FAISS store operations, index file writing, and duplicates removal."""
    manager = FAISSStoreManager()

    docs = [
        Document(id="doc_a", content="The capital of France is Paris.", metadata={"priority": 1}),
        Document(id="doc_b", content="The capital of Germany is Berlin.", metadata={"priority": 2})
    ]

    # Create and Save
    manager.create_index(docs)
    manager.save_index(temp_dir)

    # Check files exist
    assert os.path.exists(os.path.join(temp_dir, "index.faiss"))
    assert os.path.exists(os.path.join(temp_dir, "index.pkl"))

    # Load in new manager
    new_manager = FAISSStoreManager()
    success = new_manager.load_index(temp_dir)
    assert success is True
    assert new_manager.db is not None

    # Test Deduplication: Add "doc_a" again with updated text
    updated_docs = [
        Document(id="doc_a", content="Paris is the beautiful capital of France.", metadata={"priority": 1})
    ]
    new_manager.add_documents(updated_docs)

    # Search for Paris - should return doc_a with the new text
    results = new_manager.db.similarity_search("Paris", k=1)
    assert results[0].metadata["chunk_id"] == "doc_a"
    assert "beautiful" in results[0].page_content

    # Total document count in docstore should still be 2 (no duplicate vector added)
    assert len(new_manager.db.index_to_docstore_id) == 2


def test_ranker() -> None:
    """Test multi-attribute sorting logic in SearchResultRanker."""
    ranker = SearchResultRanker()
    from langchain_core.documents import Document as LCDocument

    # Mock candidate tuple: (LCDocument, L2/CosineDistance)
    # Since COSINE strategy is set: CosineSimilarity = 1 - score
    candidates = [
        (LCDocument(page_content="Text A", metadata={"chunk_id": "c1", "document_id": "d1", "priority": 1, "chunk_index": 0}), 0.1),  # CosineSimilarity = 0.9
        (LCDocument(page_content="Text B", metadata={"chunk_id": "c2", "document_id": "d2", "priority": 5, "chunk_index": 0}), 0.1),  # CosineSimilarity = 0.9 (Higher Priority)
        (LCDocument(page_content="Text C", metadata={"chunk_id": "c3", "document_id": "d1", "priority": 1, "chunk_index": 1}), 0.1),  # CosineSimilarity = 0.9 (Later Index)
        (LCDocument(page_content="Text D", metadata={"chunk_id": "c4", "document_id": "d3", "priority": 3, "chunk_index": 0}), 0.3),  # CosineSimilarity = 0.7
    ]

    ranked = ranker.rank_results("query", candidates, min_similarity=0.5)

    assert len(ranked) == 4
    # The first item must be Text B because it has the highest priority (5) among those with similarity 0.9
    assert ranked[0].chunk_id == "c2"
    # The second should be Text A (priority 1, index 0)
    assert ranked[1].chunk_id == "c1"
    # The third should be Text C (priority 1, index 1)
    assert ranked[2].chunk_id == "c3"
    # The last should be Text D (similarity 0.7)
    assert ranked[3].chunk_id == "c4"


def test_api_endpoints(client) -> None:
    """Integration test for POST /index and POST /search API routes."""
    # 1. Trigger Re-indexing
    index_response = client.post("/index")
    assert index_response.status_code == 200
    index_data = index_response.json()
    assert index_data["status"] == "success"
    assert index_data["documents_processed"] > 0
    assert index_data["chunks_created"] > 0

    # 2. Run Search Query
    search_payload = {
        "query": "Can read-only users create API keys?",
        "top_k": 3,
        "min_similarity": 0.3
    }
    search_response = client.post("/search", json=search_payload)
    assert search_response.status_code == 200
    search_data = search_response.json()
    assert search_data["query"] == "Can read-only users create API keys?"
    assert "latency_ms" in search_data
    assert len(search_data["results"]) > 0

    # Top hit should be the relevant section in system documentation
    top_hit = search_data["results"][0]
    assert "API key" in top_hit["text"] or "read-only" in top_hit["text"]
    assert top_hit["confidence_score"] >= 0.3
