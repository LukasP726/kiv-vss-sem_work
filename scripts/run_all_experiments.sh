#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <netlogo_path_or_launcher>"
  exit 1
fi

NETLOGO_PATH="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/run_all_baselines.sh" "$NETLOGO_PATH"
"$SCRIPT_DIR/run_extended_experiments.sh" "$NETLOGO_PATH"

echo "All experiments and aggregations completed."
