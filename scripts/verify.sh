#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTEST_BIN="./.venv/bin/pytest"

if [[ ! -x "$PYTEST_BIN" ]]; then
  echo "Missing pytest in ./.venv/bin/pytest" >&2
  exit 1
fi

echo "[verify] static checks skipped (ruff/mypy not wired in repo gate yet)"
echo "[verify] tests"
exec "$PYTEST_BIN" tests -q
