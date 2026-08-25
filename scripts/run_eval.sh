#!/usr/bin/env bash
# Execute Evaluation Benchmark
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

echo "📊 Running ManufacturingAgent Evaluation Benchmark..."
export PYTHONPATH="$DIR:$PYTHONPATH"
python3 evaluation/run_evaluation.py
