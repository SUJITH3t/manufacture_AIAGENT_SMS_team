"""
ManufacturingAgent Document Loaders
Loads industrial markdown specifications, SOPs, and guideline documents.
"""

import os
from pathlib import Path
from typing import List, Dict, Any


class Document:
    """Represents an ingested manufacturing engineering document."""
    def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
        self.page_content = page_content
        self.metadata = metadata or {}

    def __repr__(self):
        source = self.metadata.get("source", "unknown")
        return f"<Document source='{source}' length={len(self.page_content)}>"


class ManufacturingDocLoader:
    """Loads all manufacturing markdown and text files from a directory."""

    def __init__(self, documents_dir: str):
        self.documents_dir = Path(documents_dir)

    def load(self) -> List[Document]:
        """Load all .md and .txt documents from the directory."""
        if not self.documents_dir.exists():
            raise FileNotFoundError(f"Documents directory '{self.documents_dir}' does not exist.")

        documents: List[Document] = []
        for file_path in sorted(self.documents_dir.glob("*.md")):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            title = file_path.stem.replace("_", " ").title()
            doc = Document(
                page_content=content,
                metadata={
                    "source": file_path.name,
                    "file_path": str(file_path.absolute()),
                    "title": title,
                    "char_count": len(content)
                }
            )
            documents.append(doc)

        return documents
