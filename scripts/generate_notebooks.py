"""
Script to generate all 6 Jupyter Notebooks for ManufacturingAgent with rich markdown and executable cells.
"""

import json
import os
from pathlib import Path


def create_notebook(cells, filepath):
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.13"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)
    print(f"Generated notebook: {filepath}")


def make_md_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.split("\n")]
    }


def make_code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.split("\n")]
    }


def generate_all_notebooks():
    # -------------------------------------------------------------
    # 01_data_exploration.ipynb
    # -------------------------------------------------------------
    nb01_cells = [
        make_md_cell("# Notebook 01: Manufacturing Sensor Data Exploration & Baselines\n\n**ManufacturingAgent: Evidence-Grounded Decision Support**\n\nThis notebook inspects the machine fleet telemetry database, analyzes sensor parameter distributions (Temperature, Vibration RMS, Pressure, Speed, Humidity), and establishes engineering baseline thresholds."),
        make_code_cell("import sys\nimport os\nimport json\nimport pandas as pd\n\n# Ensure backend is in path\nsys.path.insert(0, os.path.abspath('..'))\n\n# Load machine fleet database\nwith open('../data/machines.json', 'r') as f:\n    data = json.load(f)\n\nmachines = data['machines']\nprint(f'Total Fleet Machines: {len(machines)}')\nfor m_id, info in machines.items():\n    print(f\"{m_id}: {info['model']} at {info['location']} - Status: {info['current_sensors']['status']}\")"),
        make_md_cell("## Extract Telemetry Dataframe"),
        make_code_cell("records = []\nfor m_id, info in machines.items():\n    row = {'machine_id': m_id, 'model': info['model'], 'location': info['location']}\n    row.update(info['current_sensors'])\n    records.append(row)\n\ndf = pd.DataFrame(records)\ndf"),
        make_md_cell("## Historical Telemetry Trends for M-101 and M-201"),
        make_code_cell("history_records = []\nfor m_id, info in machines.items():\n    for h in info.get('history', []):\n        h_row = {'machine_id': m_id, 'model': info['model']}\n        h_row.update(h)\n        history_records.append(h_row)\n\nhdf = pd.DataFrame(history_records)\nhdf")
    ]
    create_notebook(nb01_cells, "notebooks/01_data_exploration.ipynb")

    # -------------------------------------------------------------
    # 02_rag_pipeline.ipynb
    # -------------------------------------------------------------
    nb02_cells = [
        make_md_cell("# Notebook 02: Manufacturing RAG Pipeline (Load, Split, Embed, Retrieve)\n\nDemonstrates document ingestion from engineering markdown manuals, semantic text chunking, embedding generation, vector similarity indexing, and structured citation retrieval."),
        make_code_cell("import sys\nimport os\nsys.path.insert(0, os.path.abspath('..'))\n\nfrom backend.app.rag.loaders import ManufacturingDocLoader\nfrom backend.app.rag.splitter import ManufacturingTextSplitter\nfrom backend.app.rag.embeddings import FastDeterministicEmbeddings\nfrom backend.app.rag.retriever import ManufacturingRetriever\n\n# 1. Load documents\nloader = ManufacturingDocLoader('../data/documents')\ndocs = loader.load()\nprint(f'Loaded {len(docs)} documents:')\nfor d in docs:\n    print(f\"- {d.metadata['source']} ({d.metadata['char_count']} chars)\")"),
        make_md_cell("## 2. Text Splitting and Metadata Preservation"),
        make_code_cell("splitter = ManufacturingTextSplitter(chunk_size=450, chunk_overlap=60)\nchunks = splitter.split_documents(docs)\nprint(f'Generated {len(chunks)} semantic chunks.')\nprint('Sample chunk metadata:', chunks[0].metadata)\nprint('Sample chunk text:\\n', chunks[0].page_content[:200])"),
        make_md_cell("## 3. Querying the Retriever"),
        make_code_cell("retriever = ManufacturingRetriever(documents_dir='../data/documents', top_k=3)\nquery = 'ISO 10816 vibration velocity limits for spindle bearing fault'\nevidence = retriever.retrieve(query, k=3)\n\nprint(f'Retrieved {len(evidence)} evidence chunks for: \"{query}\"\\n')\nfor i, ev in enumerate(evidence):\n    print(f\"[{i+1}] Source: {ev['source']} (Section: {ev['section']}, Score: {ev['relevance']})\")\n    print(f\"    {ev['content'][:180]}...\\n\")")
    ]
    create_notebook(nb02_cells, "notebooks/02_rag_pipeline.ipynb")

    # -------------------------------------------------------------
    # 03_provider_comparison.ipynb
    # -------------------------------------------------------------
    nb03_cells = [
        make_md_cell("# Notebook 03: LLM Provider Abstraction & Latency Comparison\n\nEvaluates the multi-provider routing architecture across Ollama, Groq, and Local Fallback."),
        make_code_cell("import sys\nimport os\nimport time\nsys.path.insert(0, os.path.abspath('..'))\n\nfrom backend.app.providers.router import ProviderRouter, get_llm_provider\n\nrouter = ProviderRouter()\n\n# Check availability\nfor p_name in ['fallback', 'ollama', 'groq']:\n    prov = router.get_provider(p_name)\n    avail = prov.is_available()\n    print(f'Provider: {p_name:<10} | Name: {prov.get_provider_name():<25} | Available: {avail}')"),
        make_md_cell("## Test Inference Latency on Benchmark Prompt"),
        make_code_cell("test_prompt = 'Analyze machine spindle temperature 78.5C with vibration 2.8 mm/s.'\nfor p_name in ['fallback']:\n    prov = router.get_provider(p_name)\n    t0 = time.time()\n    response = prov.generate(test_prompt)\n    dur = time.time() - t0\n    print(f'Provider [{p_name}] Latency: {dur:.4f}s')\n    print(f'Response excerpt:\\n{response[:250]}...\\n')")
    ]
    create_notebook(nb03_cells, "notebooks/03_provider_comparison.ipynb")

    # -------------------------------------------------------------
    # 04_langgraph_agent.ipynb
    # -------------------------------------------------------------
    nb04_cells = [
        make_md_cell("# Notebook 04: LangGraph Agent Workflow Execution\n\nStep-by-step trace through the LangGraph StateGraph nodes:\n`START` -> `validate_input` -> `risk_assessment` -> `route_request` -> `retrieve_evidence` -> `analyze_sensor_data` -> `generate_draft` -> `review_node` -> `final_response` -> `END`"),
        make_code_cell("import sys\nimport os\nimport json\nsys.path.insert(0, os.path.abspath('..'))\n\nfrom backend.app.agent.graph import build_manufacturing_graph, ManufacturingAgentExecutor\n\nexecutor = ManufacturingAgentExecutor()\n\n# Execute Normal Case\nstate = executor.run(\n    machine_id='M-101',\n    user_query='Assess machine operating parameters.',\n    sensor_data={'temperature': 52.0, 'vibration': 0.85, 'pressure': 5.4, 'speed': 4500, 'humidity': 45.0, 'status': 'RUNNING'}\n)\n\nprint('Execution Completed!')\nprint('Risk Level:', state['risk_level'])\nprint('Review Status:', state['review_status'])\nprint('Selected Tools:', state['selected_tools'])\nprint('Evidence Count:', len(state['evidence']))\nprint('Final Response:\\n', state['final_response'])")
    ]
    create_notebook(nb04_cells, "notebooks/04_langgraph_agent.ipynb")

    # -------------------------------------------------------------
    # 05_agent_evaluation.ipynb
    # -------------------------------------------------------------
    nb05_cells = [
        make_md_cell("# Notebook 05: Agent Evaluation and Performance Metrics\n\nExecutes automated benchmark evaluation over the 24 curated test cases and visualizes accuracy, escalation precision, and latency distributions."),
        make_code_cell("import sys\nimport os\nimport pandas as pd\nsys.path.insert(0, os.path.abspath('..'))\n\nfrom evaluation.run_evaluation import run_benchmark\n\n# Execute benchmark\nrun_benchmark('../evaluation/evaluation_dataset.json', provider='fallback')\n\n# Load and display generated results dataframe\ndf_results = pd.read_csv('../evaluation/evaluation_results.csv')\ndf_results.head(10)"),
        make_md_cell("## Evaluation Summary Table by Category"),
        make_code_cell("summary = df_results.groupby('category').agg({\n    'risk_match': 'mean',\n    'escalation_match': 'mean',\n    'evidence_count': 'mean',\n    'latency_sec': 'mean'\n})\nsummary['risk_accuracy_%'] = summary['risk_match'] * 100\nsummary['escalation_accuracy_%'] = summary['escalation_match'] * 100\nsummary[['risk_accuracy_%', 'escalation_accuracy_%', 'evidence_count', 'latency_sec']]")
    ]
    create_notebook(nb05_cells, "notebooks/05_agent_evaluation.ipynb")

    # -------------------------------------------------------------
    # 06_capstone_demo.ipynb
    # -------------------------------------------------------------
    nb06_cells = [
        make_md_cell("# Notebook 06: Capstone Demonstration (4 Core Scenarios & Human Review)\n\nDemonstrating all four project scenarios:\n1. **Normal Case**: Baseline steady-state milling\n2. **Edge Case**: Borderline thermal drift requiring monitoring\n3. **Failure Case**: Hardware sensor open-circuit fault\n4. **High-Risk Case**: Severe dual-parameter excursion with live Human Escalation and Sign-Off"),
        make_code_cell("import sys\nimport os\nsys.path.insert(0, os.path.abspath('..'))\n\nfrom backend.app.agent.graph import ManufacturingAgentExecutor\nfrom backend.app.agent.review import get_review_manager\n\nexecutor = ManufacturingAgentExecutor()\nmanager = get_review_manager()\n\ndef print_scenario_result(title, state):\n    print('=' * 75)\n    print(f'SCENARIO: {title}')\n    print('=' * 75)\n    print(f\"INPUT: Machine {state['machine_id']} | Query: {state['user_query']}\")\n    print(f\"RISK LEVEL: {state['risk_level']} (Reason: {state['risk_reason']})\")\n    print(f\"TOOLS INVOKED: {state['selected_tools']}\")\n    print(f\"EVIDENCE COUNT: {len(state['evidence'])}\")\n    print(f\"REVIEW STATUS: {state['review_status']}\")\n    print('-' * 75)\n    print(f\"FINAL RESULT:\\n{state['final_response'][:400]}...\\n\")"),
        make_md_cell("## 1. Normal Case Demonstration"),
        make_code_cell("res_normal = executor.run(\n    machine_id='M-101',\n    user_query='Check if current telemetry conforms to ISO 10816 standards.',\n    sensor_data={'temperature': 52.4, 'vibration': 0.85, 'pressure': 5.4, 'speed': 4500, 'status': 'RUNNING'}\n)\nprint_scenario_result('Case 1: Normal Operation', res_normal)"),
        make_md_cell("## 2. Edge Case Demonstration"),
        make_code_cell("res_edge = executor.run(\n    machine_id='M-102',\n    user_query='Spindle temperature reached 74.8C. Advise on inspection.',\n    sensor_data={'temperature': 74.8, 'vibration': 2.65, 'pressure': 4.1, 'speed': 6200, 'status': 'WARN_TELEMETRY'}\n)\nprint_scenario_result('Case 2: Edge Condition', res_edge)"),
        make_md_cell("## 3. Failure Case Demonstration"),
        make_code_cell("res_fail = executor.run(\n    machine_id='M-301',\n    user_query='Sensor reporting negative numbers.',\n    sensor_data={'temperature': -999.0, 'vibration': 0.0, 'pressure': -1.0, 'speed': 0, 'status': 'SENSOR_FAULT'}\n)\nprint_scenario_result('Case 3: Sensor Fault / Non-physical Telemetry', res_fail)"),
        make_md_cell("## 4. High-Risk Case Demonstration & Human Review Sign-off"),
        make_code_cell("res_high = executor.run(\n    machine_id='M-201',\n    user_query='Extreme chatter, 89.6C heat and 5.42 mm/s vibration reported during heavy titanium turn.',\n    sensor_data={'temperature': 89.6, 'vibration': 5.42, 'pressure': 2.9, 'speed': 8200, 'status': 'ELEVATED_RISK'}\n)\nprint_scenario_result('Case 4: High Risk Escalation', res_high)\n\n# Inspect Pending Ticket\npending = manager.list_pending_tickets()\nprint(f'Pending Tickets in Human Review Queue: {len(pending)}')\nticket_id = res_high['request_id']\nprint(f'Reviewing Ticket ID: {ticket_id}')\n\n# Human Engineer Sign-off Action\nsignoff = manager.submit_decision(\n    request_id=ticket_id,\n    decision='approve',\n    notes='Confirmed severe bearing raceway spalling. Dispatched mechanical overhaul technician with replacement bearing pack.',\n    reviewer_id='CHIEF_MAINT_ENG_402'\n)\nprint(f'Human Decision Recorded: {signoff.decision.upper()} by {signoff.reviewer_id}')\nprint(f'Notes: {signoff.notes}')")
    ]
    create_notebook(nb06_cells, "notebooks/06_capstone_demo.ipynb")


if __name__ == "__main__":
    generate_all_notebooks()
