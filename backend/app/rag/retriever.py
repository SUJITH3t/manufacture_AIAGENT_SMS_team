"""
ManufacturingAgent RAG Retriever
High-level retriever that coordinates loading, chunking, indexing, and relevance querying.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from backend.app.rag.loaders import ManufacturingDocLoader, Document
from backend.app.rag.splitter import ManufacturingTextSplitter
from backend.app.rag.embeddings import BaseEmbeddingProvider, FastDeterministicEmbeddings, get_embedding_provider
from backend.app.rag.vectorstore import ManufacturingVectorStore

logger = logging.getLogger(__name__)


class ManufacturingRetriever:
    """End-to-end RAG retriever for manufacturing SOPs and manuals."""

    def __init__(
        self,
        documents_dir: str = "./data/documents",
        persist_dir: str = "./data/chroma_db",
        embedding_provider: Optional[BaseEmbeddingProvider] = None,
        top_k: int = 4
    ):
        self.documents_dir = documents_dir
        self.persist_dir = persist_dir
        self.embedding_provider = embedding_provider or FastDeterministicEmbeddings()
        self.top_k = top_k
        self.vector_store = ManufacturingVectorStore(
            persist_dir=persist_dir,
            embedding_provider=self.embedding_provider
        )
        self._is_indexed = False
        self._ensure_indexed()

    def _ensure_indexed(self):
        """Index documents if not already in memory/disk."""
        if self._is_indexed:
            return

        # Attempt to load from disk first
        if self.vector_store._local_store.load_from_disk() and len(self.vector_store._local_store.documents) > 0:
            self._is_indexed = True
            logger.info(f"Loaded {len(self.vector_store._local_store.documents)} indexed chunks from disk.")
            return

        # Otherwise build index from docs directory
        self.build_index()

    def build_index(self):
        """Load all docs, split, embed, and store in vector store."""
        if not os.path.exists(self.documents_dir):
            logger.warning(f"Documents directory {self.documents_dir} does not exist. Index is empty.")
            return

        loader = ManufacturingDocLoader(self.documents_dir)
        raw_docs = loader.load()
        splitter = ManufacturingTextSplitter(chunk_size=500, chunk_overlap=80)
        chunks = splitter.split_documents(raw_docs)

        self.vector_store.add_documents(chunks)
        self._is_indexed = True
        logger.info(f"Successfully built RAG index with {len(chunks)} chunks from {len(raw_docs)} documents.")

    def retrieve(self, query: str, k: Optional[int] = None, min_relevance: float = 0.10) -> List[Dict[str, Any]]:
        """
        Retrieve relevant evidence items formatted as structured dicts:
        [{ 'source': str, 'content': str, 'relevance': float, 'title': str, 'section': str }]
        """
        if not query or not query.strip():
            return []

        search_k = k or self.top_k
        results = self.vector_store.similarity_search_with_score(query, k=search_k)

        evidence_items: List[Dict[str, Any]] = []
        for doc, score in results:
            if score >= min_relevance:
                evidence_items.append({
                    "source": doc.metadata.get("source", "manufacturing_manual.md"),
                    "title": doc.metadata.get("title", "Industrial Guideline"),
                    "section": doc.metadata.get("section_title", "General"),
                    "content": doc.page_content.strip(),
                    "relevance": round(float(score), 4)
                })

        return evidence_items
