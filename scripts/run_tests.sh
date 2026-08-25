#!/usr/bin/env bash
# Execute pytest suite
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

echo "🧪 Running ManufacturingAgent Pytest Suite..."
export PYTHONPATH="$DIR:$PYTHONPATH"
pytest tests/ -v
