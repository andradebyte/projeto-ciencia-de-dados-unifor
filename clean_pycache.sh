#!/usr/bin/env bash
set -euo pipefail

find . -type d -name "__pycache__" -not -path "./.venv/*" -exec rm -rf {} +
find . -type f -name "*.py[cod]" -not -path "./.venv/*" -delete

echo "pycache removido."
