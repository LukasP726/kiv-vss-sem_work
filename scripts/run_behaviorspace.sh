#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 4 ]]; then
  echo "Usage: $0 <netlogo_path> <model_path> <experiment_name> <output_csv>"
  exit 1
fi

NETLOGO_PATH="$1"
MODEL_PATH="$2"
EXPERIMENT_NAME="$3"
OUTPUT_CSV="$4"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [[ "$MODEL_PATH" != /* ]]; then
  MODEL_PATH="$ROOT_DIR/${MODEL_PATH#./}"
fi
if [[ "$OUTPUT_CSV" != /* ]]; then
  OUTPUT_CSV="$ROOT_DIR/${OUTPUT_CSV#./}"
fi

if [[ ! -f "$MODEL_PATH" ]]; then
  echo "Model not found: $MODEL_PATH"
  exit 1
fi

resolve_launcher() {
  local input="$1"
  if [[ -d "$input" ]]; then
    local candidate="$input/netlogo-headless.sh"
    [[ -f "$candidate" ]] && { echo "$candidate"; return; }
  fi
  if [[ -f "$input" ]]; then
    if [[ "$input" == *"netlogo-headless.sh" ]]; then
      echo "$input"
      return
    fi
    local parent
    parent="$(dirname "$input")"
    local candidate="$parent/netlogo-headless.sh"
    [[ -f "$candidate" ]] && { echo "$candidate"; return; }
  fi
  echo ""
}

LAUNCHER="$(resolve_launcher "$NETLOGO_PATH")"
if [[ -z "$LAUNCHER" ]]; then
  echo "Cannot resolve netlogo-headless.sh from: $NETLOGO_PATH"
  exit 1
fi

OUT_DIR="$(dirname "$OUTPUT_CSV")"
mkdir -p "$OUT_DIR"
rm -f "$OUTPUT_CSV"

STDOUT_LOG="${OUTPUT_CSV%.*}.stdout.log"
STDERR_LOG="${OUTPUT_CSV%.*}.stderr.log"

echo "Running BehaviorSpace experiment..."
echo "Model: $MODEL_PATH"
echo "Experiment: $EXPERIMENT_NAME"
echo "Output: $OUTPUT_CSV"
echo "Launcher: $LAUNCHER"

"$LAUNCHER" \
  --headless \
  --model "$MODEL_PATH" \
  --experiment "$EXPERIMENT_NAME" \
  --table "$OUTPUT_CSV" \
  1>"$STDOUT_LOG" \
  2>"$STDERR_LOG"

if [[ ! -f "$OUTPUT_CSV" ]]; then
  echo "BehaviorSpace did not create output CSV: $OUTPUT_CSV"
  echo "See logs: $STDOUT_LOG and $STDERR_LOG"
  exit 1
fi

LINE_COUNT="$(wc -l < "$OUTPUT_CSV")"
if [[ "$LINE_COUNT" -lt 2 ]]; then
  echo "BehaviorSpace output has no data rows: $OUTPUT_CSV"
  echo "See logs: $STDOUT_LOG and $STDERR_LOG"
  exit 1
fi

echo "Done."
