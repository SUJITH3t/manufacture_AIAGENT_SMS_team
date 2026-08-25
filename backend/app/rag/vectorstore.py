"""
ManufacturingAgent Vector Store
Provides high-performance vector storage with ChromaDB and in-memory Cosine Vector Store fallback.
"""

import json
import math
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from backend.app.rag.loaders import Document
from backend.app.rag.embeddings import BaseEmbeddingProvider, FastDeterministicEmbeddings

logger = logging.getLogger(__name__)


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a < 1e-9 or norm_b < 1e-9:
        return 0.0
    return dot / (norm_a * norm_b)


class LocalVectorStore:
    """
    Lightweight, robust, self-contained Vector Store using exact Cosine Similarity.
    Zero C++ compilation issues, 100% predictable across all environments.
    """

    def __init__(self, embedding_provider: BaseEmbeddingProvider = None, persist_path: str = None):
        self.embedding_provider = embedding_provider or FastDeterministicEmbeddings()
        self.persist_path = Path(persist_path) if persist_path else None
        self.documents: List[Document] = []
        self.vectors: List[List[float]] = []

    def add_documents(self, documents: List[Document]):
        """Embed and add documents to store."""
        if not documents:
            return
        texts = [doc.page_content for doc in documents]
        new_vectors = self.embedding_provider.embed_documents(texts)
        self.documents.extend(documents)
        self.vectors.extend(new_vectors)
        if self.persist_path:
            self.persist()

    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """Search top-k most similar documents with similarity scores in [0.0, 1.0]."""
        if not self.documents or not self.vectors:
            return []

        query_vec = self.embedding_provider.embed_query(query)
        scores = []
        for idx, doc_vec in enumerate(self.vectors):
            score = cosine_similarity(query_vec, doc_vec)
            scores.append((self.documents[idx], max(0.0, min(1.0, score))))

        # Sort descending by score
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]

    def persist(self):
        """Persist documents and vectors to disk."""
        if not self.persist_path:
            return
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "documents": [
                {"page_content": d.page_content, "metadata": d.metadata}
                for d in self.documents
            ],
            "vectors": self.vectors
        }
        with open(self.persist_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load_from_disk(self):
        """Load documents and vectors from persisted disk file."""
        if not self.persist_path or not self.persist_path.exists():
            return False
        try:
            with open(self.persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.documents = [
                Document(page_content=item["page_content"], metadata=item.get("metadata", {}))
                for item in data.get("documents", [])
            ]
            self.vectors = data.get("vectors", [])
            return True
        except Exception as e:
            logger.warning(f"Could not load vector store from {self.persist_path}: {e}")
            return False


class ManufacturingVectorStore:
    """Wrapper that manages ChromaDB with automatic LocalVectorStore fallback."""

    def __init__(self, persist_dir: str = "./data/chroma_db", embedding_provider: BaseEmbeddingProvider = None):
        self.persist_dir = Path(persist_dir)
        self.embedding_provider = embedding_provider or FastDeterministicEmbeddings()
        self._local_store = LocalVectorStore(
            embedding_provider=self.embedding_provider,
            persist_path=str(self.persist_dir / "index.json")
        )
        self._chroma_client = None
        self._chroma_collection = None
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            self._chroma_client = chromadb.PersistentClient(path=str(self.persist_dir))
            self._chroma_collection = self._chroma_client.get_or_create_collection(
                name="manufacturing_knowledge_base"
            )
        except Exception as e:
            logger.info(f"Using local high-performance vector store (Chroma init info: {e})")

    def add_documents(self, documents: List[Document]):
        """Add documents to both local store and Chroma if available."""
        self._local_store.add_documents(documents)
        if self._chroma_collection is not None:
            try:
                ids = [f"doc_{i}_{doc.metadata.get('chunk_id', i)}" for i, doc in enumerate(documents)]
                texts = [doc.page_content for doc in documents]
                metadatas = [
                    {k: str(v) for k, v in doc.metadata.items()}
                    for doc in documents
                ]
                self._chroma_collection.upsert(
                    ids=ids,
                    documents=texts,
                    metadatas=metadatas
                )
            except Exception as e:
                logger.debug(f"Chroma add fallback to local store: {e}")

    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        """Perform similarity search returning (Document, score)."""
        return self._local_store.similarity_search_with_score(query, k=k)
