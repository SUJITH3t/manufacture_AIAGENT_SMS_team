# ManufacturingAgent: Complete Setup & Execution Guide

Follow these exact steps to set up, configure, index, test, evaluate, and launch the ManufacturingAgent application.

---

## 1. Prerequisites
- **Python**: Version 3.10, 3.11, 3.12, or 3.13
- **Git** (optional)
- **Ollama** (optional, for local LLM inference) or **Groq API Key** (optional, for cloud LLM inference)

---

## 2. Environment Setup & Dependency Installation

### Step 2.1: Create Virtual Environment
```bash
# Navigate to project root
cd /Users/assujith/ManufacturingAgent

# Create python virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS / Linux:
source venv/bin/activate
# On Windows (PowerShell):
# .\venv\Scripts\Activate.ps1
```

### Step 2.2: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 3. Environment Configuration (`.env`)

Copy the `.env.example` template to `.env`:
```bash
cp .env.example .env
```

Edit `.env` to configure your preferred LLM provider:

### Option A: Local Fallback Mode (Zero external dependencies, works out of the box)
```ini
LLM_PROVIDER=fallback
```

### Option B: Local Ollama Mode
1. Download and start Ollama from [ollama.ai](https://ollama.ai).
2. Pull your model:
   ```bash
   ollama pull llama3:8b
   ```
3. Update `.env`:
   ```ini
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3:8b
   ```

### Option C: Groq Cloud Mode
1. Obtain an API key from [console.groq.com](https://console.groq.com).
2. Update `.env`:
   ```ini
   LLM_PROVIDER=groq
   GROQ_API_KEY=gsk_your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

---

## 4. Build the RAG Knowledge Base Index

Index the 6 manufacturing markdown manuals into the vector store:
```bash
python3 scripts/build_rag_index.py
```

---

## 5. Run Automated Tests

Execute all 37 unit and integration tests with pytest:
```bash
pytest tests/ -v
# or via script:
./scripts/run_tests.sh
```

---

## 6. Run Benchmark Evaluation

Execute the 24-case benchmark dataset to generate metrics CSV and markdown report:
```bash
python3 evaluation/run_evaluation.py
# or via script:
./scripts/run_eval.sh
```

The generated artifacts will be located at:
- `evaluation/evaluation_results.csv`
- `evaluation/evaluation_report.md`

---

## 7. Start the FastAPI Backend Server

Launch the REST API server on `http://127.0.0.1:8000`:
```bash
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
# or via script:
./scripts/run_backend.sh
```

Interactive API documentation will be accessible at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## 8. Start the Streamlit Web Dashboard

In a new terminal window (with virtual environment activated):
```bash
streamlit run frontend/app.py --server.port 8501
# or via script:
./scripts/run_frontend.sh
```

Open your browser to `http://localhost:8501` to access the interactive dashboard.

---

## 9. Run Jupyter Notebooks

Launch Jupyter Lab / Notebook to interact with the 6 step-by-step notebooks:
```bash
jupyter lab
# or:
jupyter notebook
```

Navigate to `notebooks/` and run in numerical order:
1. `01_data_exploration.ipynb`
2. `02_rag_pipeline.ipynb`
3. `03_provider_comparison.ipynb`
4. `04_langgraph_agent.ipynb`
5. `05_agent_evaluation.ipynb`
6. `06_capstone_demo.ipynb`
