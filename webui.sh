#!/bin/bash
set -e
CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "***** Current directory: $CURRENT_DIR *****"
export PYTHONPATH="$CURRENT_DIR"

MPT_WEBUI_HOST="${MPT_WEBUI_HOST:-0.0.0.0}"
MPT_WEBUI_PORT="${MPT_WEBUI_PORT:-8080}"

PYTHON_CMD=""
if [ -f "$CURRENT_DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$CURRENT_DIR/.venv/bin/python"
elif command -v uv &>/dev/null; then
    PYTHON_CMD="uv run python"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "***** Python not found. Please install dependencies first. *****"
    exit 1
fi

echo "***** Starting MoneyPrinterTurbo at http://$MPT_WEBUI_HOST:$MPT_WEBUI_PORT *****"
$PYTHON_CMD main.py
