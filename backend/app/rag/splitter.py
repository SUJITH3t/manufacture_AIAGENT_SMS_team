"""
ManufacturingAgent Document Splitter
Splits manufacturing documents into coherent semantic chunks preserving section context.
"""

import re
from typing import List, Dict, Any
from backend.app.rag.loaders import Document


class ManufacturingTextSplitter:
    """Splits documents by markdown headers or character windows with overlap."""

    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split a list of Document objects into smaller chunk Documents."""
        chunks: List[Document] = []
        for doc in documents:
            doc_chunks = self.split_text(doc.page_content, doc.metadata)
            chunks.extend(doc_chunks)
        return chunks

    def split_text(self, text: str, base_metadata: Dict[str, Any] = None) -> List[Document]:
        """Split single document text into chunk documents."""
        base_meta = base_metadata.copy() if base_metadata else {}
        
        # Split by top-level or second-level markdown headers
        sections = re.split(r'(?=\n#{1,3}\s+)', text.strip())
        
        chunks: List[Document] = []
        chunk_idx = 0

        for section in sections:
            section_str = section.strip()
            if not section_str:
                continue

            # Extract section title if present
            header_match = re.match(r'^(#{1,3})\s+(.+)$', section_str, re.MULTILINE)
            section_title = header_match.group(2).strip() if header_match else "General"

            # If section is small enough, keep as single chunk
            if len(section_str) <= self.chunk_size:
                meta = base_meta.copy()
                meta.update({
                    "chunk_id": chunk_idx,
                    "section_title": section_title,
                    "chunk_length": len(section_str)
                })
                chunks.append(Document(page_content=section_str, metadata=meta))
                chunk_idx += 1
            else:
                # Sub-split long section with overlap
                start = 0
                while start < len(section_str):
                    end = min(start + self.chunk_size, len(section_str))
                    # Avoid cutting in the middle of a word if possible
                    if end < len(section_str):
                        last_space = section_str.rfind(' ', start, end)
                        if last_space > start + (self.chunk_size // 2):
                            end = last_space

                    chunk_text = section_str[start:end].strip()
                    if chunk_text:
                        meta = base_meta.copy()
                        meta.update({
                            "chunk_id": chunk_idx,
                            "section_title": section_title,
                            "chunk_length": len(chunk_text)
                        })
                        chunks.append(Document(page_content=chunk_text, metadata=meta))
                        chunk_idx += 1

                    if end >= len(section_str):
                        break
                    start = max(start + 1, end - self.chunk_overlap)

        return chunks
