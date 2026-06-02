#!/usr/bin/env bash
# Local full ingest: same sequence as .github/workflows/ingest.yml
#   4.0 scrape → 4.1 normalize → 4.2 chunk+embed → 4.3 Chroma upsert
#
# Usage (from repo root):
#   ./scripts/run-ingest-local.sh
#   ./scripts/run-ingest-local.sh /path/to/custom.log
#
# Logs default to data/logs/ingest-<UTC-timestamp>.log (stdout + stderr).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
LOGFILE="${1:-$ROOT/data/logs/ingest-${TS_UTC}.log}"
mkdir -p "$(dirname "$LOGFILE")"

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi

# Match CI: cache Hugging Face models under the repo (optional if already set)
export HF_HOME="${HF_HOME:-$ROOT/.cache/huggingface}"
mkdir -p "$HF_HOME"

log() {
  # shellcheck disable=SC2320
  echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOGFILE"
}

run_phase() {
  local title="$1" module="$2"
  log "========== START: $title =========="
  log "Command: $PYTHON -m $module"
  set +e
  $PYTHON -m "$module" 2>&1 | tee -a "$LOGFILE"
  local st="${PIPESTATUS[0]}"
  set -e
  if [[ "$st" -ne 0 ]]; then
    log "========== FAIL: $title (exit $st) =========="
    exit "$st"
  fi
  log "========== OK: $title =========="
}

log "Ingest log file: $LOGFILE"
log "Repo root: $ROOT"
log "Python: $PYTHON ($($PYTHON --version 2>&1))"
log "HF_HOME=$HF_HOME"

run_phase "Phase 4.0 — Scrape URL registry" "ingest.phases.phase_4_0_scheduler_scraping"
run_phase "Phase 4.1 — Normalize HTML" "ingest.phases.phase_4_1_normalize"
run_phase "Phase 4.2 — Chunk and embed (bge-small-en-v1.5)" "ingest.phases.phase_4_2_chunk_embedding"
run_phase "Phase 4.3 — Upsert to local Chroma" "ingest.phases.phase_4_3_vector_index"

if [[ "${INGEST_PRUNE_SKIP:-}" =~ ^(1|true|yes)$ ]]; then
  log "INGEST_PRUNE_SKIP set — skipping prune of old run dirs / logs"
else
  run_phase "Prune — keep latest run only (+ ingest logs cap)" "ingest.prune_old_runs"
fi

log "Full ingest finished successfully."
