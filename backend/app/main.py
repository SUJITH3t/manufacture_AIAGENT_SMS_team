"""
ManufacturingAgent FastAPI Application Server
Entrypoint providing telemetry analysis, evidence-grounded decision support, and human review endpoints.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from backend.app.config import get_settings
from backend.app.agent.graph import ManufacturingAgentExecutor
from backend.app.agent.review import get_review_manager, ReviewDecisionRequest
from backend.app.tools.sensor_tool import get_sensor_data
from backend.app.tools.calculator_tool import calculate, CalculatorInput
from backend.app.rag.retriever import ManufacturingRetriever

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ManufacturingAgent.API")

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Evidence-Grounded Manufacturing Monitoring and Decision-Support Agent with Risk Routing and Human Review",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize singletons
agent_executor = ManufacturingAgentExecutor()
review_manager = get_review_manager()


# -------------------------------------------------------------
# Structured Telemetry Logging Middleware (Excludes Secrets)
# -------------------------------------------------------------
@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    duration = round((time.time() - start_time) * 1000, 2)

    logger.info(
        f"[HTTP Audit] method={request.method} path={request.url.path} "
        f"status={response.status_code} latency_ms={duration}"
    )
    return response


# -------------------------------------------------------------
# Request / Response Schemas
# -------------------------------------------------------------
class AnalyzeRequest(BaseModel):
    machine_id: str = Field(..., description="Target machine ID, e.g., 'M-101'")
    user_query: str = Field(..., description="Operator question or diagnostic inquiry")
    sensor_data: Optional[Dict[str, Any]] = Field(default=None, description="Optional real-time telemetry dictionary")
    provider: Optional[str] = Field(default=None, description="'ollama', 'groq', or 'fallback'")


class AnalyzeResponse(BaseModel):
    request_id: str
    machine_id: str
    risk_level: str
    risk_reason: str
    selected_tools: List[str]
    retrieved_evidence_count: int
    evidence: List[Dict[str, Any]]
    analysis: str
    draft_response: str
    review_status: str
    review_reason: str
    final_response: str
    provider: str
    latency_seconds: float
    error: Optional[str] = None


class ReviewActionResponse(BaseModel):
    success: bool
    request_id: str
    machine_id: str
    decision: str
    notes: Optional[str]
    reviewer_id: Optional[str]
    resolved_at: float
    message: str


# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------
@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint confirming API status and active provider."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "default_provider": settings.LLM_PROVIDER,
        "timestamp": time.time()
    }


@app.post("/analyze", response_model=AnalyzeResponse, tags=["Agent Workflow"])
def analyze_telemetry(req: AnalyzeRequest):
    """
    Run full LangGraph manufacturing decision-support pipeline:
    Input Validation -> Risk Assessment -> RAG Evidence Retrieval -> Sensor Analysis -> Draft -> Safety Review -> Human Escalation / Final Response.
    """
    if not req.machine_id or not req.machine_id.strip():
        raise HTTPException(status_code=400, detail="Machine ID cannot be empty.")
    if not req.user_query or not req.user_query.strip():
        raise HTTPException(status_code=400, detail="User query cannot be empty.")

    provider_to_use = req.provider or settings.LLM_PROVIDER

    try:
        final_state = agent_executor.run(
            machine_id=req.machine_id,
            user_query=req.user_query,
            sensor_data=req.sensor_data,
            provider=provider_to_use
        )

        # Audit Log (safe metrics only)
        logger.info(
            f"[Agent Execution Completed] request_id={final_state.get('request_id')} "
            f"provider={final_state.get('provider')} "
            f"risk_level={final_state.get('risk_level')} "
            f"tools={final_state.get('selected_tools')} "
            f"retrieval_count={len(final_state.get('evidence', []))} "
            f"review_status={final_state.get('review_status')} "
            f"latency={final_state.get('latency')}s"
        )

        return AnalyzeResponse(
            request_id=final_state.get("request_id"),
            machine_id=final_state.get("machine_id"),
            risk_level=final_state.get("risk_level", "NORMAL"),
            risk_reason=final_state.get("risk_reason", ""),
            selected_tools=final_state.get("selected_tools", []),
            retrieved_evidence_count=len(final_state.get("evidence", [])),
            evidence=final_state.get("evidence", []),
            analysis=final_state.get("analysis", ""),
            draft_response=final_state.get("draft_response", ""),
            review_status=final_state.get("review_status", "approved"),
            review_reason=final_state.get("review_reason", ""),
            final_response=final_state.get("final_response", ""),
            provider=final_state.get("provider", provider_to_use),
            latency_seconds=final_state.get("latency", 0.0),
            error=final_state.get("error")
        )
    except Exception as e:
        logger.error(f"Error during agent execution: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal agent pipeline error: {str(e)}")


@app.post("/review/{request_id}", response_model=ReviewActionResponse, tags=["Human Review"])
def submit_human_review(request_id: str, body: ReviewDecisionRequest):
    """
    Human Review Sign-off Endpoint:
    Allows a human engineer to approve, reject, or request revision on escalated cases.
    """
    ticket = review_manager.get_ticket(request_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Human review ticket '{request_id}' not found.")

    try:
        updated_ticket = review_manager.submit_decision(
            request_id=request_id,
            decision=body.decision,
            notes=body.notes or "",
            reviewer_id=body.reviewer_id or "HUMAN_ENG_01"
        )
        return ReviewActionResponse(
            success=True,
            request_id=updated_ticket.request_id,
            machine_id=updated_ticket.machine_id,
            decision=updated_ticket.decision,
            notes=updated_ticket.notes,
            reviewer_id=updated_ticket.reviewer_id,
            resolved_at=updated_ticket.resolved_at,
            message=f"Human review decision '{updated_ticket.decision}' successfully recorded."
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@app.get("/review/pending", tags=["Human Review"])
def get_pending_reviews():
    """Retrieve list of all tickets awaiting human sign-off."""
    pending = review_manager.list_pending_tickets()
    return {
        "pending_count": len(pending),
        "tickets": pending
    }


@app.get("/review/{request_id}", tags=["Human Review"])
def get_review_ticket(request_id: str):
    """Retrieve specific review ticket details and audit status."""
    ticket = review_manager.get_ticket(request_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Review ticket '{request_id}' not found.")
    return ticket


@app.get("/machines", tags=["Telemetry Tools"])
def list_machines():
    """List available simulated machines in fleet."""
    import json
    import os
    if os.path.exists("./data/machines.json"):
        with open("./data/machines.json", "r") as f:
            return json.load(f)
    return {"machines": {}}


@app.get("/machines/{machine_id}", tags=["Telemetry Tools"])
def get_machine_telemetry(machine_id: str):
    """Fetch real-time telemetry reading for given machine."""
    res = get_sensor_data(machine_id)
    if not res.get("success"):
        raise HTTPException(status_code=404, detail=res.get("error"))
    return res


@app.post("/tools/calculate", tags=["Telemetry Tools"])
def calculate_expression(req: CalculatorInput):
    """Execute safe mathematical calculation."""
    res = calculate(req.expression)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("error"))
    return res


def start():
    """Start uvicorn server programmatically."""
    uvicorn.run(
        "backend.app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=False
    )


if __name__ == "__main__":
    start()
