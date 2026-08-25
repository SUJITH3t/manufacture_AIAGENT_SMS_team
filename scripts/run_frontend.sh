#!/usr/bin/env bash
# Start ManufacturingAgent Streamlit Frontend Dashboard
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

echo "⚙️ Starting ManufacturingAgent Streamlit Web Dashboard on port 8501..."
export PYTHONPATH="$DIR:$PYTHONPATH"
streamlit run frontend/app.py --server.port 8501 --server.headless false
