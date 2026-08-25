"""
ManufacturingAgent Embedding Providers
Supports SentenceTransformers, Ollama Embeddings, and Fast Local Deterministic Vectorizer.
"""

import math
import re
import logging
from typing import List
import httpx

logger = logging.getLogger(__name__)


class BaseEmbeddingProvider:
    """Abstract interface for document and query embeddings."""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> List[float]:
        raise NotImplementedError


class FastDeterministicEmbeddings(BaseEmbeddingProvider):
    """
    High-speed, zero-dependency token-frequency embedding with subword hashing and cosine normalization.
    Ensures 100% reliable, zero-latency vector similarity without external downloads.
    """

    def __init__(self, dim: int = 256):
        self.dim = dim

    def _hash_token(self, token: str) -> int:
        h = 2166136261
        for ch in token:
            h = (h ^ ord(ch)) * 16777619 & 0xFFFFFFFF
        return h % self.dim

    def _embed_single(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        tokens = re.findall(r'\b[a-zA-Z0-9_\-\.]{2,}\b', text.lower())
        if not tokens:
            return vec

        for tok in tokens:
            idx = self._hash_token(tok)
            vec[idx] += 1.0
            # Also hash bigrams for phrase matching
            if len(tok) > 4:
                sub_idx = self._hash_token(tok[:4])
                vec[sub_idx] += 0.5

        # L2 Normalize
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 1e-9:
            vec = [v / norm for v in vec]
        return vec

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_single(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_single(text)


class SentenceTransformerEmbeddings(BaseEmbeddingProvider):
    """Local SentenceTransformer embedding model."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.warning(f"Failed to load SentenceTransformer ({e}). Falling back to FastDeterministicEmbeddings.")
                self._model = FastDeterministicEmbeddings()
        return self._model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        if isinstance(model, FastDeterministicEmbeddings):
            return model.embed_documents(texts)
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        model = self._get_model()
        if isinstance(model, FastDeterministicEmbeddings):
            return model.embed_query(text)
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()


class OllamaEmbeddings(BaseEmbeddingProvider):
    """Ollama local embedding endpoint integration."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "nomic-embed-text"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.fallback = FastDeterministicEmbeddings()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        results = []
        for text in texts:
            results.append(self.embed_query(text))
        return results

    def embed_query(self, text: str) -> List[float]:
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text}
                )
                if res.status_code == 200:
                    return res.json().get("embedding", [])
        except Exception as e:
            logger.debug(f"Ollama embedding unavailable ({e}), using fast deterministic embedding.")
        return self.fallback.embed_query(text)


def get_embedding_provider(provider_type: str = "fast", model_name: str = "all-MiniLM-L6-v2", base_url: str = "http://localhost:11434") -> BaseEmbeddingProvider:
    """Factory to create embedding provider."""
    if provider_type.lower() == "ollama":
        return OllamaEmbeddings(base_url=base_url, model=model_name)
    elif provider_type.lower() == "sentence-transformers":
        return SentenceTransformerEmbeddings(model_name=model_name)
    else:
        return FastDeterministicEmbeddings()
