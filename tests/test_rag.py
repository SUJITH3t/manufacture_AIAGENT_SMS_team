"""
Unit Tests for ManufacturingAgent RAG Subsystem
"""

import os
import pytest
from backend.app.rag.loaders import ManufacturingDocLoader
from backend.app.rag.splitter import ManufacturingTextSplitter
from backend.app.rag.embeddings import FastDeterministicEmbeddings, SentenceTransformerEmbeddings
from backend.app.rag.vectorstore import LocalVectorStore, cosine_similarity
from backend.app.rag.retriever import ManufacturingRetriever


def test_document_loader():
    """Test loading manufacturing markdown documentation."""
    loader = ManufacturingDocLoader("./data/documents")
    docs = loader.load()
    assert len(docs) >= 6
    sources = [d.metadata["source"] for d in docs]
    assert "machine_manual.md" in sources
    assert "vibration_guidelines.md" in sources
    assert "safety_procedures.md" in sources


def test_text_splitter():
    """Test splitting documents into chunks with headers and section metadata."""
    loader = ManufacturingDocLoader("./data/documents")
    docs = loader.load()
    splitter = ManufacturingTextSplitter(chunk_size=400, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    
    assert len(chunks) > len(docs)
    for c in chunks:
        assert "source" in c.metadata
        assert "section_title" in c.metadata
        assert len(c.page_content) > 0


def test_cosine_similarity_math():
    """Test mathematical accuracy of cosine similarity calculation."""
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]
    assert pytest.approx(cosine_similarity(v1, v2), 0.001) == 1.0
    assert pytest.approx(cosine_similarity(v1, v3), 0.001) == 0.0


def test_fast_embeddings():
    """Test fast deterministic embedding generation."""
    embedder = FastDeterministicEmbeddings(dim=128)
    texts = ["spindle temperature overheating", "hydraulic line pressure drop"]
    vectors = embedder.embed_documents(texts)
    assert len(vectors) == 2
    assert len(vectors[0]) == 128
    
    q_vec = embedder.embed_query("spindle thermal limit")
    assert len(q_vec) == 128


def test_local_vector_store():
    """Test local vector store indexing and query retrieval."""
    loader = ManufacturingDocLoader("./data/documents")
    docs = loader.load()
    splitter = ManufacturingTextSplitter(chunk_size=500, chunk_overlap=60)
    chunks = splitter.split_documents(docs)

    store = LocalVectorStore()
    store.add_documents(chunks)

    results = store.similarity_search_with_score("ISO 10816 vibration severity class", k=3)
    assert len(results) == 3
    doc, score = results[0]
    assert score > 0.0
    assert "vibration" in doc.page_content.lower() or "iso" in doc.page_content.lower()


def test_end_to_end_retriever():
    """Test full retriever returning structured citations."""
    retriever = ManufacturingRetriever(documents_dir="./data/documents")
    evidence = retriever.retrieve("hydraulic pressure relief valve cavitation", k=3)
    assert len(evidence) > 0
    first = evidence[0]
    assert "source" in first
    assert "content" in first
    assert "relevance" in first
    assert first["relevance"] >= 0.0
