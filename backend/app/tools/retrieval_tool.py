"""
ManufacturingAgent Retrieval Tool
Retrieves relevant manufacturing guidelines, technical manuals, and SOP evidence for a given query.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.rag.retriever import ManufacturingRetriever


class RetrievalToolInput(BaseModel):
    query: str = Field(description="Search query describing the component, fault mode, or guideline needed")
    top_k: int = Field(default=4, description="Number of document chunks to retrieve")


_GLOBAL_RETRIEVER: Optional[ManufacturingRetriever] = None


def get_retriever() -> ManufacturingRetriever:
    """Singleton getter for the manufacturing RAG retriever."""
    global _GLOBAL_RETRIEVER
    if _GLOBAL_RETRIEVER is None:
        _GLOBAL_RETRIEVER = ManufacturingRetriever()
    return _GLOBAL_RETRIEVER


def retrieve_manufacturing_guidelines(query: str, top_k: int = 4) -> Dict[str, Any]:
    """
    Retrieve authoritative manufacturing SOP and manual passages matching the query.
    Returns structured list of evidence items with source citations and relevance scores.
    """
    if not query or not query.strip():
        return {
            "success": False,
            "query": query,
            "evidence_count": 0,
            "evidence": [],
            "error": "Query string cannot be empty."
        }

    try:
        retriever = get_retriever()
        evidence_items = retriever.retrieve(query=query, k=top_k)
        return {
            "success": True,
            "query": query,
            "evidence_count": len(evidence_items),
            "evidence": evidence_items,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "query": query,
            "evidence_count": 0,
            "evidence": [],
            "error": f"Retrieval failed: {str(e)}"
        }
