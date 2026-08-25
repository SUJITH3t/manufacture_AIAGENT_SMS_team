#!/usr/bin/env bash
# Start ManufacturingAgent FastAPI Backend
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

echo "🚀 Starting ManufacturingAgent FastAPI Backend on port 8000..."
export PYTHONPATH="$DIR:$PYTHONPATH"
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
