"""Development-only sensitivity using archived, dated inputs."""

import csv
import hashlib
import json
from datetime import date

from backtest import summarize
from evaluate import DATA, lock_inputs
from signal_test import DEFENSIVE_EQUITY, read_months, simulate_rules


def development_sensitivity(lag_days, cost_bp):
    if lag_days not in (1, 7) or not 0 <= cost_bp <= 50:
        raise ValueError("Use 1 or 7 calendar days and 0 to 50 basis points.")
    _, locked_files = lock_inputs()
    with (DATA / "sessions.csv").open(newline="", encoding="utf-8") as file:
        sessions = {row["month"]: date.fromisoformat(row["last_session"])
                    for row in csv.DictReader(file)}
    if lag_days == 7:
        folder = DATA / "sensitivity"
        hashes = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))["files"]
    else:
        folder = DATA / "alfred"
        hashes = {key.rsplit("/", 1)[-1]: value for key, value in locked_files.items()
                  if key.startswith("data/alfred/")}

    def load_vintage(cutoff):
        name = f"{cutoff}.csv"
        content = (folder / name).read_bytes().replace(b"\r\n", b"\n")
        if hashlib.sha256(content).hexdigest() != hashes.get(name):
            raise ValueError(f"Sensitivity input hash mismatch: {name}")
        return content.decode("utf-8")

    months, _ = read_months(DATA / "verified_prices.csv", sessions, load_vintage,
                            start="2021-10", end="2025-09", lag_days=lag_days)
    return {name: {**summarize(rows),
                   "defensive_requests": sum(row.target == DEFENSIVE_EQUITY for row in rows)}
            for name, rows in simulate_rules(months, cost=cost_bp / 10_000).items()}
