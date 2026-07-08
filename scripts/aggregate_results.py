import argparse
import csv
import math
from collections import defaultdict


def parse_args():
    parser = argparse.ArgumentParser(description="Aggregate BehaviorSpace CSV results.")
    parser.add_argument("--input", required=True, help="Input CSV path")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument(
        "--group-by",
        required=False,
        default="",
        help="Comma-separated columns to group by (optional)",
    )
    parser.add_argument(
        "--metrics",
        required=True,
        help="Comma-separated numeric metric columns to aggregate",
    )
    return parser.parse_args()


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def mean(values):
    return sum(values) / len(values) if values else float("nan")


def stddev(values):
    if len(values) < 2:
        return 0.0
    m = mean(values)
    var = sum((x - m) ** 2 for x in values) / (len(values) - 1)
    return math.sqrt(var)


def percentile(values, p):
    if not values:
        return float("nan")
    vals = sorted(values)
    if len(vals) == 1:
        return vals[0]
    idx = (len(vals) - 1) * p
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return vals[int(idx)]
    return vals[lo] * (hi - idx) + vals[hi] * (idx - lo)


def main():
    args = parse_args()
    group_cols = [c.strip() for c in args.group_by.split(",") if c.strip()]
    metric_cols = [c.strip() for c in args.metrics.split(",") if c.strip()]

    groups = defaultdict(lambda: {m: [] for m in metric_cols})

    with open(args.input, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    header_idx = None
    for i, row in enumerate(rows):
        if any(cell.strip() == "[run number]" for cell in row):
            header_idx = i
            break

    if header_idx is None:
        raise RuntimeError(
            "Could not find data header '[run number]' in input CSV. "
            "Make sure this is a BehaviorSpace table export."
        )

    header = rows[header_idx]
    data_rows = rows[header_idx + 1 :]
    index = {name: idx for idx, name in enumerate(header)}

    for raw in data_rows:
        if not raw or all(not cell.strip() for cell in raw):
            continue
        row = {name: raw[idx] if idx < len(raw) else "" for name, idx in index.items()}
        key = tuple(row.get(col, "") for col in group_cols) if group_cols else ("__all__",)
        for metric in metric_cols:
            value = to_float(row.get(metric))
            if value is not None:
                groups[key][metric].append(value)

    fieldnames = list(group_cols) if group_cols else ["group"]
    for metric in metric_cols:
        fieldnames.extend(
            [
                f"{metric}_n",
                f"{metric}_mean",
                f"{metric}_std",
                f"{metric}_p25",
                f"{metric}_p50",
                f"{metric}_p75",
            ]
        )

    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for key, metric_map in groups.items():
            if group_cols:
                out = {group_cols[i]: key[i] for i in range(len(group_cols))}
            else:
                out = {"group": "all_runs"}
            for metric in metric_cols:
                values = metric_map[metric]
                out[f"{metric}_n"] = len(values)
                out[f"{metric}_mean"] = f"{mean(values):.6f}" if values else ""
                out[f"{metric}_std"] = f"{stddev(values):.6f}" if values else ""
                out[f"{metric}_p25"] = f"{percentile(values, 0.25):.6f}" if values else ""
                out[f"{metric}_p50"] = f"{percentile(values, 0.50):.6f}" if values else ""
                out[f"{metric}_p75"] = f"{percentile(values, 0.75):.6f}" if values else ""
            writer.writerow(out)

    print(f"Saved aggregated results to: {args.output}")


if __name__ == "__main__":
    main()
