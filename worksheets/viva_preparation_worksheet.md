# ManufacturingAgent: College Viva & Technical Defense Preparation Worksheet

This worksheet details key architectural questions, design trade-offs, and technical rationale for presenting the ManufacturingAgent capstone project during a college viva or engineering review.

---

## 1. Core Architecture & Safety Boundaries

### Q1: What is the exact purpose and safety boundary of the ManufacturingAgent?
> **Answer**:
> ManufacturingAgent is a **bounded decision-support prototype** for industrial asset monitoring. It analyzes real-time sensor telemetry, cross-references authoritative engineering SOPs and manuals via RAG, evaluates operational risk (NORMAL, EDGE, HIGH), and drafts evidence-grounded recommendations.
> 
> **Safety Boundary**: The agent has **zero physical actuation authority**. It does not issue PLC commands, execute G-code, alter machine feeds, shut down equipment, or override safety interlocks. All actions require certified human engineer verification and execution.

### Q2: Why use LangGraph instead of a simple linear chain or single LLM prompt?
> **Answer**:
> 1. **State Machine Control**: LangGraph provides explicit state persistence (`AgentState`) across validation, risk assessment, RAG retrieval, analysis, drafting, and review.
> 2. **Dynamic Conditional Routing**: Enables branching based on telemetry risk tiers:
>    - `NORMAL`: Completes with baseline manual citations.
>    - `EDGE`: Expands retrieval for multi-variable edge cases.
>    - `HIGH`: Automatically halts autonomous flow and routes to the **Human Review Node**.
> 3. **Auditing and Self-Correction**: The Review Node checks for grounding and non-actuation boundaries before final output generation.

---

## 2. Multi-Provider LLM Abstraction & RAG Design

### Q3: How is the multi-provider LLM router designed?
> **Answer**:
> We created an abstract `BaseLLMProvider` interface implemented by `OllamaProvider` (local open-weight LLMs like Llama 3 / Mistral), `GroqProvider` (high-throughput cloud inference), and `FallbackDeterministicProvider` (offline rule-guided generator). The `ProviderRouter` dynamically resolves the provider at runtime based on environment variables or API parameters without modifying graph code.

### Q4: How does the RAG pipeline prevent hallucinations?
> **Answer**:
> 1. **Domain-Specific Chunking**: Documents (manuals, ISO 10816 vibration standards, hydraulic guidelines) are parsed with markdown section headers retained in chunk metadata.
> 2. **Relevance Scoring & Filtering**: Vector similarity matches query intent to specific manual sections.
> 3. **Format Separation**: The draft prompt enforces a strict distinction between **Retrieved Grounded Evidence** and **Model Diagnostic Recommendations**.
> 4. **Review Node Gate**: Drafts lacking evidence or containing unsupported physical claims are flagged for revision or human review.

---

## 3. Human-in-the-Loop Workflow

### Q5: How does the Human-in-the-Loop review mechanism operate?
> **Answer**:
> When a case is classified as `HIGH` risk (e.g. Temperature > 82°C or Vibration > 3.8 mm/s), the `human_review_node` registers an escalation ticket in `HumanReviewManager` and appends a prominent `HUMAN REVIEW REQUIRED` banner.
> Human operators interact through the Streamlit Human Review Portal or REST endpoint `POST /review/{request_id}` to submit `approve`, `reject`, or `request_revision` decisions along with inspection directives.

---

## 4. Viva Quick-Reference Summary Table

| Module | Implementation | Key Responsibility |
| :--- | :--- | :--- |
| **Backend Framework** | FastAPI + Pydantic | REST API, async endpoints, audit middleware |
| **Workflow Engine** | LangGraph StateGraph | Deterministic multi-node execution and conditional routing |
| **RAG Vector Store** | ChromaDB / Local Cosine | Ingestion, chunking, and similarity retrieval |
| **Telemetry Tools** | Pydantic Tool Functions | Real-time sensor lookup, history, safe math calculator, risk scorer |
| **Frontend** | Streamlit | Real-time telemetry dashboard, risk badges, evidence viewer, human sign-off portal |
| **Testing & Eval** | pytest (37 tests) + Benchmark (24 cases) | 100% test coverage and formal metrics report |
