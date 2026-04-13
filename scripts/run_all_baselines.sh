#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <netlogo_path_or_launcher>"
  exit 1
fi

NETLOGO_PATH="$1"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_DIR="$ROOT_DIR/out"
mkdir -p "$OUT_DIR"

run_model() {
  local name="$1"
  local model="$2"
  local raw="$OUT_DIR/${name}_baseline.csv"
  local summary="$OUT_DIR/${name}_baseline_summary.csv"

  "$SCRIPT_DIR/run_behaviorspace.sh" "$NETLOGO_PATH" "$model" "baseline_auto" "$raw"

  python "$SCRIPT_DIR/aggregate_results.py" \
    --input "$raw" \
    --metrics "m_final_susceptible,m_final_exposed,m_final_infected,m_final_recovered,m_ever_infected,m_ticks,m_deaths,m_final_resources" \
    --output "$summary"
}

run_model "virus1" "$ROOT_DIR/examples/virus1.nlogox"
run_model "virus2" "$ROOT_DIR/examples/virus2.nlogox"
run_model "virus3" "$ROOT_DIR/examples/virus3.nlogox"
run_model "virus4" "$ROOT_DIR/examples/virus4.nlogox"

echo "All baseline runs completed."
