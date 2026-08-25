"""
ManufacturingAgent Typed State
Defines the schema for state passing through all LangGraph nodes.
"""

from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """Structured State for ManufacturingAgent LangGraph workflow."""
    request_id: str
    machine_id: str
    sensor_data: Dict[str, Any]
    user_query: str
    risk_level: str               # "NORMAL", "EDGE", "HIGH"
    risk_reason: str
    tool_required: bool
    selected_tools: List[str]
    retrieved_documents: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]] # [{"source": str, "content": str, "relevance": float}]
    analysis: str
    draft_response: str
    review_status: str            # "approved", "revision_required", "human_review"
    review_reason: str
    human_decision: Optional[str] # "approve", "reject", "request_revision"
    human_notes: Optional[str]
    final_response: str
    provider: str
    error: Optional[str]
    latency: Optional[float]
    iteration_count: Optional[int]
