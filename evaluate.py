"""Reproduce the frozen Project 2 test entirely from committed inputs."""

import argparse
import csv
import hashlib
import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

from signal_test import compare, decision, read_months

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
HOLDOUT_START = "2025-10"


def lock_inputs():
    manifest_bytes = (DATA / "input_manifest.json").read_bytes().replace(b"\r\n", b"\n")
    manifest = json.loads(manifest_bytes)
    for name, digest in manifest["files"].items():
        content = (ROOT / name).read_bytes().replace(b"\r\n", b"\n")
        if hashlib.sha256(content).hexdigest() != digest:
            raise ValueError(f"Frozen input hash mismatch: {name}")
    return hashlib.sha256(manifest_bytes).hexdigest(), manifest["files"]


def run():
    input_hash, frozen_files = lock_inputs()
    with (DATA / "sessions.csv").open(newline="", encoding="utf-8") as handle:
        sessions = {row["month"]: date.fromisoformat(row["last_session"]) for row in csv.DictReader(handle)}

    def vintage(cutoff):
        name = f"data/alfred/{cutoff}.csv"
        if name not in frozen_files:
            raise ValueError(f"Unlisted vintage for approved cutoff {cutoff}.")
        return (ROOT / name).read_text(encoding="utf-8")

    months, audit = read_months(DATA / "verified_prices.csv", sessions, vintage,
                                start="2021-10", end="2026-09")
    if len(months) != 60 or sum(m.month >= HOLDOUT_START for m in months) != 12:
        raise ValueError("Frozen split must contain 48 development and 12 holdout months.")
    results, series = compare(months, holdout_start=HOLDOUT_START)
    verdict, reasons = decision(results, series, HOLDOUT_START)
    return {
        "manifest_sha256": input_hash,
        "development": "2021-10 to 2025-09",
        "holdout": "2025-10 to 2026-09",
        "holdout_start": HOLDOUT_START,
        "results": results,
        "decision": verdict,
        "reasons": reasons,
        "monthly": {name: [asdict(row) for row in rows] for name, rows in series.items()},
        "vintage_audit": [{"return_month": month, "trade_date": trade, "cutoff": cutoff,
                           "rate_pair": asdict(info) if info else None}
                          for month, trade, cutoff, info in audit],
    }


def report(output):
    lines = [
        "# FEDFUNDS overlay — Project 2 results",
        "",
        f"Development: {output['development']}. Historical holdout: {output['holdout']}.",
        "Costs: 10 bp per 100% one-way turnover. Calendar-year turnover cap: 25% for allocated mixes.",
        "",
        "| Period | Rule | Gross return | Net return | Monthly-close max drawdown | Turnover | Avg. VT weight | Defensive requests | Cap-limited months |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for period in ("development", "holdout"):
        for name, periods in output["results"].items():
            row = periods[period]
            lines.append(f"| {period.title()} | {name} | {row['gross']:.2%} | {row['net']:.2%} | "
                         f"{row['max_drawdown']:.2%} | {row['turnover']:.2%} | "
                         f"{row['average_equity']:.2%} | {row['defensive_requests']} | {row['cap_limited_months']} |")
    lines.extend(["", f"**Decision: {output['decision']}.** " + "; ".join(output["reasons"]) + ".",
                  "", "Returns are compounded for each period. Drawdown uses net monthly closes, "
                  "with each period starting at 1. Turnover in the table groups by return period; "
                  "the actual limit is enforced by trade date. The historical holdout does not establish "
                  "the foundation's rolling five-year real return or suitability.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Save the reproducible Markdown and JSON outputs.")
    options = parser.parse_args()
    output = run()
    markdown = report(output)
    if options.write:
        folder = ROOT / "output"
        folder.mkdir(exist_ok=True)
        (folder / "holdout.md").write_text(markdown, encoding="utf-8")
        (folder / "holdout.json").write_text(json.dumps(output, indent=2, default=str) + "\n", encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()
