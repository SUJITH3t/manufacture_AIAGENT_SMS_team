"""
ManufacturingAgent RAG Index Builder
Loads all markdown documents from data/documents, splits into semantic chunks, and builds vector store index.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.rag.retriever import ManufacturingRetriever


def main():
    print("=" * 60)
    print("🔧 Building ManufacturingAgent RAG Knowledge Base Index")
    print("=" * 60)

    docs_dir = str(PROJECT_ROOT / "data" / "documents")
    persist_dir = str(PROJECT_ROOT / "data" / "chroma_db")

    retriever = ManufacturingRetriever(documents_dir=docs_dir, persist_dir=persist_dir)
    retriever.build_index()

    print("\n✅ RAG Index successfully generated and verified.")
    print("=" * 60)


if __name__ == "__main__":
    main()
