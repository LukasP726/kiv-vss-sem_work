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

"$SCRIPT_DIR/run_behaviorspace.sh" "$NETLOGO_PATH" "$ROOT_DIR/examples/virus1.nlogox" "ofat_transmission_auto" "$OUT_DIR/virus1_ofat_transmission.csv"
python "$SCRIPT_DIR/aggregate_results.py" --input "$OUT_DIR/virus1_ofat_transmission.csv" --group-by "transmission-prob" --metrics "m_ticks,m_deaths,m_final_infected" --output "$OUT_DIR/virus1_ofat_transmission_summary.csv"

"$SCRIPT_DIR/run_behaviorspace.sh" "$NETLOGO_PATH" "$ROOT_DIR/examples/virus2.nlogox" "capacity_overload_grid_auto" "$OUT_DIR/virus2_capacity_grid.csv"
python "$SCRIPT_DIR/aggregate_results.py" --input "$OUT_DIR/virus2_capacity_grid.csv" --group-by "healthcare-capacity,overload-multiplier" --metrics "m_deaths,m_final_infected" --output "$OUT_DIR/virus2_capacity_grid_summary.csv"

"$SCRIPT_DIR/run_behaviorspace.sh" "$NETLOGO_PATH" "$ROOT_DIR/examples/virus3.nlogox" "resources_grid_auto" "$OUT_DIR/virus3_resources_grid.csv"
python "$SCRIPT_DIR/aggregate_results.py" --input "$OUT_DIR/virus3_resources_grid.csv" --group-by "resource-stock,resource-regeneration,treatment-cost" --metrics "m_deaths,m_final_resources,m_final_infected" --output "$OUT_DIR/virus3_resources_grid_summary.csv"

"$SCRIPT_DIR/run_behaviorspace.sh" "$NETLOGO_PATH" "$ROOT_DIR/examples/virus4.nlogox" "strategy_grid_auto" "$OUT_DIR/virus4_strategy_grid.csv"
python "$SCRIPT_DIR/aggregate_results.py" --input "$OUT_DIR/virus4_strategy_grid.csv" --group-by "strategy-mode,high-risk-share,vaccination-rate" --metrics "m_deaths,m_final_infected" --output "$OUT_DIR/virus4_strategy_grid_summary.csv"

echo "Extended experiments completed."
