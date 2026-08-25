"""
ManufacturingAgent Application Configuration
Loads settings from environment variables using Pydantic Settings.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global configuration settings for ManufacturingAgent."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Provider
    LLM_PROVIDER: str = "fallback"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"

    # Groq
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Server
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 8501

    # RAG
    CHROMA_PERSIST_DIR: str = "./data/chroma_db"
    DOCUMENTS_DIR: str = "./data/documents"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    MAX_RETRIEVAL_RESULTS: int = 4
    SIMILARITY_THRESHOLD: float = 0.35

    # Safety
    ENABLE_HUMAN_REVIEW_AUTO_QUEUE: bool = True
    APP_NAME: str = "ManufacturingAgent: Decision Support"
    VERSION: str = "1.0.0"


_settings = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
