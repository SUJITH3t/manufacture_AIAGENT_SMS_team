"""
ManufacturingAgent Streamlit Web Dashboard
Evidence-Grounded Manufacturing Monitoring & Decision-Support Interface with Human-in-the-Loop Review.
"""

import streamlit as st
import httpx
import json
import time
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="ManufacturingAgent | Decision-Support",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Industrial Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&family=Outfit:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stCode, code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 24px;
        border-radius: 14px;
        border: 1px solid #334155;
        margin-bottom: 24px;
        color: #f8fafc;
    }
    
    .main-title {
        font-size: 26px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #38bdf8;
        margin: 0;
    }
    
    .sub-title {
        font-size: 14px;
        color: #94a3b8;
        margin-top: 4px;
    }

    .safety-banner {
        background-color: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        border-radius: 8px;
        padding: 12px 16px;
        color: #fca5a5;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 20px;
    }

    .badge-normal {
        background-color: #064e3b;
        color: #6ee7b7;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
        border: 1px solid #059669;
    }

    .badge-edge {
        background-color: #78350f;
        color: #fde68a;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
        border: 1px solid #d97706;
    }

    .badge-high {
        background-color: #7f1d1d;
        color: #fca5a5;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        display: inline-block;
        border: 1px solid #dc2626;
        animation: pulse 2s infinite;
    }

    .evidence-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }

    .evidence-title {
        color: #38bdf8;
        font-weight: 600;
        font-size: 14px;
    }

    .evidence-meta {
        color: #64748b;
        font-size: 12px;
        margin-bottom: 8px;
    }

    .metric-card {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Preset telemetry profiles
PRESETS = {
    "Normal Operation (M-101)": {
        "machine_id": "M-101",
        "temperature": 52.4,
        "vibration": 0.85,
        "pressure": 5.4,
        "speed": 4500,
        "humidity": 45.0,
        "query": "Assess machine health and verify if current vibration conforms to ISO 10816."
    },
    "Edge Case: Elevated Temp (M-102)": {
        "machine_id": "M-102",
        "temperature": 74.8,
        "vibration": 2.65,
        "pressure": 4.1,
        "speed": 6200,
        "humidity": 52.0,
        "query": "Spindle temperature is trending upward. What is the recommended inspection procedure?"
    },
    "High Risk: Severe Vibration & Heat (M-201)": {
        "machine_id": "M-201",
        "temperature": 89.6,
        "vibration": 5.42,
        "pressure": 2.9,
        "speed": 8200,
        "humidity": 48.0,
        "query": "Critical vibration excursion and low hydraulic pressure reported during roughing pass."
    },
    "Failure Case: Corrupt / Missing Sensor (M-301)": {
        "machine_id": "M-301",
        "temperature": -999.0,
        "vibration": 0.0,
        "pressure": -1.0,
        "speed": 0,
        "humidity": 0.0,
        "query": "Sensor telemetry is reporting negative numbers. Advise on diagnostic protocol."
    }
}

# Sidebar - Settings & Presets
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/engine.png", width=64)
    st.markdown("### Control & Configuration")
    
    provider_choice = st.selectbox(
        "LLM Provider",
        ["fallback", "ollama", "groq"],
        index=0,
        help="Select active LLM engine. 'fallback' works offline with 0 latency."
    )

    api_url = st.text_input("Backend API Base URL", value="http://127.0.0.1:8000")
    
    st.markdown("---")
    st.markdown("### Quick Diagnostic Presets")
    selected_preset_name = st.selectbox("Load Scenario Preset", list(PRESETS.keys()))
    
    if st.button("Apply Preset"):
        preset = PRESETS[selected_preset_name]
        st.session_state["machine_id"] = preset["machine_id"]
        st.session_state["temp"] = float(preset["temperature"])
        st.session_state["vib"] = float(preset["vibration"])
        st.session_state["pres"] = float(preset["pressure"])
        st.session_state["speed"] = int(preset["speed"])
        st.session_state["hum"] = float(preset["humidity"])
        st.session_state["query"] = preset["query"]
        st.rerun()

    st.markdown("---")
    st.markdown("""
    **Operational Boundaries**:
    - 🔒 Advisory Decision Support Only
    - 🚫 No Machine Actuation
    - 🚫 No PLC Override
    """)

# Main Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">ManufacturingAgent</h1>
    <div class="sub-title">Evidence-Grounded Manufacturing Monitoring and Decision-Support Agent with Risk Routing and Human Review</div>
</div>
""", unsafe_allow_html=True)

# Safety Boundary Callout
st.markdown("""
<div class="safety-banner">
    ⚠️ <strong>SAFETY BOUNDARY NOTICE</strong>: This software prototype is strictly a bounded decision-support tool. It does <strong>NOT</strong> control machinery, alter PLC codes, trigger physical shut-downs, or override plant safety systems. All recommendations must be verified and executed by certified shop-floor engineers.
</div>
""", unsafe_allow_html=True)

# Tabs
tab_monitor, tab_human_review, tab_knowledge = st.tabs([
    "📊 Telemetry Analysis & Decision Support",
    "🧑‍🔧 Human Review Portal",
    "📚 Grounded Knowledge Base"
])

# -------------------------------------------------------------
# TAB 1: Telemetry Analysis & Decision Support
# -------------------------------------------------------------
with tab_monitor:
    col_input, col_results = st.columns([1, 1.3], gap="medium")

    with col_input:
        st.markdown("#### 1. Machine Telemetry Input")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            m_id = st.text_input(
                "Machine Identifier",
                value=st.session_state.get("machine_id", "M-101")
            )
        with col_m2:
            speed_val = st.number_input(
                "Spindle Speed (RPM)",
                value=st.session_state.get("speed", 4500),
                step=100
            )

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            temp_val = st.number_input(
                "Temperature (°C)",
                value=st.session_state.get("temp", 52.4),
                format="%.1f",
                step=0.5
            )
        with col_s2:
            vib_val = st.number_input(
                "Vibration (mm/s)",
                value=st.session_state.get("vib", 0.85),
                format="%.2f",
                step=0.1
            )
        with col_s3:
            pres_val = st.number_input(
                "Pressure (bar)",
                value=st.session_state.get("pres", 5.4),
                format="%.1f",
                step=0.1
            )

        hum_val = st.slider(
            "Factory Ambient Humidity (%RH)",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state.get("hum", 45.0)
        )

        user_query_input = st.text_area(
            "Diagnostic Question / Inquiry",
            value=st.session_state.get("query", "Assess machine health and verify if current vibration conforms to ISO 10816."),
            height=100
        )

        analyze_btn = st.button("🚀 Analyze Telemetry & Generate Advisory", type="primary", use_container_width=True)

    with col_results:
        st.markdown("#### 2. Agent Assessment & Grounded Output")

        if analyze_btn:
            sensor_payload = {
                "temperature": temp_val,
                "vibration": vib_val,
                "pressure": pres_val,
                "speed": speed_val,
                "humidity": hum_val,
                "status": "RUNNING"
            }

            req_payload = {
                "machine_id": m_id,
                "user_query": user_query_input,
                "sensor_data": sensor_payload,
                "provider": provider_choice
            }

            with st.spinner("Executing LangGraph pipeline (Validation -> Risk Scoring -> RAG Retrieval -> Analysis -> Audit)..."):
                try:
                    res = httpx.post(f"{api_url}/analyze", json=req_payload, timeout=35.0)
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state["last_analysis"] = data
                    else:
                        st.error(f"API Error ({res.status_code}): {res.text}")
                except Exception as e:
                    # If backend is not running, run directly via local python executor fallback
                    try:
                        from backend.app.agent.graph import ManufacturingAgentExecutor
                        executor = ManufacturingAgentExecutor()
                        local_res = executor.run(
                            machine_id=m_id,
                            user_query=user_query_input,
                            sensor_data=sensor_payload,
                            provider=provider_choice
                        )
                        st.session_state["last_analysis"] = {
                            "request_id": local_res.get("request_id"),
                            "machine_id": local_res.get("machine_id"),
                            "risk_level": local_res.get("risk_level"),
                            "risk_reason": local_res.get("risk_reason"),
                            "selected_tools": local_res.get("selected_tools"),
                            "retrieved_evidence_count": len(local_res.get("evidence", [])),
                            "evidence": local_res.get("evidence", []),
                            "analysis": local_res.get("analysis", ""),
                            "draft_response": local_res.get("draft_response", ""),
                            "review_status": local_res.get("review_status"),
                            "review_reason": local_res.get("review_reason"),
                            "final_response": local_res.get("final_response"),
                            "provider": local_res.get("provider"),
                            "latency_seconds": local_res.get("latency", 0.0),
                            "error": local_res.get("error")
                        }
                    except Exception as le:
                        st.error(f"Execution Error: {str(le)}")

        # Display Last Analysis Results
        if "last_analysis" in st.session_state:
            res_data = st.session_state["last_analysis"]

            # 1. Risk Tier Display Banner
            risk_level = res_data.get("risk_level", "NORMAL")
            review_status = res_data.get("review_status", "approved")

            st.markdown("##### Operational Risk Evaluation")
            col_b1, col_b2, col_b3 = st.columns([1, 1, 1])

            with col_b1:
                if risk_level == "NORMAL":
                    st.markdown('<div class="badge-normal">🟢 NORMAL RISK</div>', unsafe_allow_html=True)
                elif risk_level == "EDGE":
                    st.markdown('<div class="badge-edge">🟡 EDGE CONDITION</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="badge-high">🔴 HIGH RISK: HUMAN REVIEW REQUIRED</div>', unsafe_allow_html=True)

            with col_b2:
                st.caption(f"**Review Status**: `{review_status.upper()}`")
                st.caption(f"**Tools**: `{', '.join(res_data.get('selected_tools', []))}`")

            with col_b3:
                st.caption(f"**Provider**: `{res_data.get('provider')}`")
                st.caption(f"**Latency**: `{res_data.get('latency_seconds', 0.0):.3f}s`")

            if res_data.get("risk_reason"):
                st.info(f"**Risk Rationale**: {res_data.get('risk_reason')}")

            # 2. Grounded Evidence Accordion
            evidence_list = res_data.get("evidence", [])
            with st.expander(f"📑 Retrieved RAG Evidence Chunks ({len(evidence_list)} citations)", expanded=(risk_level != "HIGH")):
                if evidence_list:
                    for i, ev in enumerate(evidence_list):
                        st.markdown(f"""
                        <div class="evidence-card">
                            <div class="evidence-title">[{i+1}] {ev.get('source')} - {ev.get('section', 'General')}</div>
                            <div class="evidence-meta">Relevance Score: {ev.get('relevance', 0.0):.4f}</div>
                            <div>{ev.get('content')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.write("No specific documents matched query thresholds.")

            # 3. Final Decision-Support Recommendation
            st.markdown("##### Generated Advisory & Action Items")
            st.markdown(res_data.get("final_response", ""))

            if risk_level == "HIGH":
                st.warning("⚠️ **Human Review Required**: This case was automatically routed to the Human Review Queue. Please navigate to the 'Human Review Portal' tab to inspect and sign off.")

# -------------------------------------------------------------
# TAB 2: Human Review Portal
# -------------------------------------------------------------
with tab_human_review:
    st.markdown("### 🧑‍🔧 Certified Maintenance Engineer Sign-Off Portal")
    st.caption("Review, approve, reject, or request revisions for high-risk or uncertain telemetry advisories.")

    # Refresh pending reviews
    if st.button("🔄 Refresh Review Queue"):
        st.rerun()

    from backend.app.agent.review import get_review_manager
    manager = get_review_manager()
    pending_tickets = manager.list_pending_tickets()
    all_tickets = manager.list_all_tickets()

    st.markdown(f"**Active Escalation Tickets**: `{len(pending_tickets)} Pending` | `{len(all_tickets)} Total`")

    if not pending_tickets:
        st.success("✅ No pending human review tickets in queue. All systems operating nominally.")
    else:
        for ticket in pending_tickets:
            with st.container():
                st.markdown(f"""
                <div style="background-color: #1e293b; border: 1px solid #dc2626; border-radius: 12px; padding: 18px; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="color: #fca5a5; margin: 0;">🚨 Escalated Ticket: {ticket.request_id} (Machine {ticket.machine_id})</h4>
                        <span class="badge-high">STATUS: {ticket.review_status.upper()}</span>
                    </div>
                    <p style="color: #cbd5e1; margin-top: 8px;"><strong>Escalation Reason:</strong> {ticket.risk_reason}</p>
                    <p style="color: #94a3b8; font-size: 13px;"><strong>Sensor Telemetry:</strong> {json.dumps(ticket.sensor_data)}</p>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"Review Draft Advisory for Ticket {ticket.request_id}"):
                    st.markdown(ticket.draft_response)

                col_dec, col_notes, col_btn = st.columns([1, 1.5, 1])
                with col_dec:
                    action_choice = st.selectbox(
                        "Engineer Action",
                        ["approve", "reject", "request_revision"],
                        key=f"dec_{ticket.request_id}"
                    )
                with col_notes:
                    notes_input = st.text_input(
                        "Sign-off Notes / Inspection Directives",
                        key=f"notes_{ticket.request_id}",
                        placeholder="e.g., Dispatched Tech #402 for manual dial test indicator runout inspection."
                    )
                with col_btn:
                    st.write("")
                    st.write("")
                    if st.button("Submit Decision", key=f"btn_{ticket.request_id}", type="primary"):
                        try:
                            # Submit via API or direct manager
                            manager.submit_decision(
                                request_id=ticket.request_id,
                                decision=action_choice,
                                notes=notes_input,
                                reviewer_id="HUMAN_OPERATOR_CHIEF"
                            )
                            st.success(f"Ticket {ticket.request_id} marked as '{action_choice}'.")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Failed to submit decision: {ex}")

    # Historical Resolved Tickets
    resolved = [t for t in all_tickets if t.decision is not None]
    if resolved:
        st.markdown("---")
        st.markdown("#### Resolved Human Review Audit Trail")
        table_data = []
        for r in resolved:
            table_data.append({
                "Request ID": r.request_id,
                "Machine ID": r.machine_id,
                "Decision": r.decision.upper(),
                "Reviewer": r.reviewer_id,
                "Notes": r.notes,
                "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r.resolved_at))
            })
        st.dataframe(pd.DataFrame(table_data), use_container_width=True)

# -------------------------------------------------------------
# TAB 3: Grounded Knowledge Base
# -------------------------------------------------------------
with tab_knowledge:
    st.markdown("### 📚 Grounded Knowledge Base Documents")
    st.caption("Authoritative manufacturing SOPs and technical manuals loaded into the RAG vector store.")

    import os
    docs_dir = "./data/documents"
    if os.path.exists(docs_dir):
        doc_files = sorted(os.listdir(docs_dir))
        selected_doc = st.selectbox("Select Document to Inspect", [f for f in doc_files if f.endswith(".md")])
        if selected_doc:
            file_path = os.path.join(docs_dir, selected_doc)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            st.markdown(content)
    else:
        st.warning("Documents directory not found.")
