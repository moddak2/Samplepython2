#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

run_semgrep() {
  "$@" scan \
    --config security/semgrep.training.yml \
    --no-git-ignore \
    --metrics=off \
    --disable-version-check \
    .
}

if command -v semgrep >/dev/null 2>&1; then
  run_semgrep semgrep
  exit 0
fi

if [[ -x ".venv/Scripts/semgrep.exe" ]]; then
  run_semgrep .venv/Scripts/semgrep.exe
  exit 0
fi

if [[ -x ".venv/bin/semgrep" ]]; then
  run_semgrep .venv/bin/semgrep
  exit 0
fi

if [[ -x ".venv/Scripts/python.exe" ]]; then
  run_semgrep .venv/Scripts/python.exe -m semgrep
  exit 0
fi

if [[ -x ".venv/bin/python" ]]; then
  run_semgrep .venv/bin/python -m semgrep
  exit 0
fi

if command -v python3 >/dev/null 2>&1; then
  run_semgrep python3 -m semgrep
  exit 0
fi

echo "semgrep not found. Install with: pip install semgrep" >&2
exit 127
