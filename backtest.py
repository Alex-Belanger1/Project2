"""Monthly, close-to-close backtest shared by the course example and Project 2."""

from dataclasses import dataclass
from datetime import date
from math import isclose, isfinite, prod


@dataclass(frozen=True)
class Month:
    month: str
    bill_return: float
    equity_return: float
    signal: float | None
    decision_date: date | None = None


@dataclass(frozen=True)
class Outcome:
    month: str
    equity_weight: float
    gross_return: float
    net_return: float
    turnover: float
    target: float | None
    cap_limited: bool
    decision_date: date | None


def simulate(months, target_weight, *, initial_equity, cost, annual_cap=None):
    """Trade from drifted weights. A missing target means hold existing holdings."""
    equity = initial_equity
    used = 0.0
    year = None
    previous = ""
    if not 0 <= initial_equity <= 1 or not 0 <= cost < 1:
        raise ValueError("Invalid initial equity weight or cost.")
    if annual_cap is not None and annual_cap < 0:
        raise ValueError("Turnover budget must be non-negative.")
    for row in months:
        if row.month <= previous:
            raise ValueError("Return months must be strictly increasing.")
        if any(not isfinite(r) or r <= -1 for r in (row.bill_return, row.equity_return)):
            raise ValueError(f"Invalid fund return in {row.month}.")
        previous = row.month
        trade_year = row.decision_date.year if row.decision_date is not None else int(row.month[:4])
        if trade_year != year:
            year, used = trade_year, 0.0
        target = target_weight(row.signal)
        if target is not None and not 0 <= target <= 1:
            raise ValueError("Target equity weight must be between 0 and 1.")
        requested = 0 if target is None else target - equity
        permitted = abs(requested) if annual_cap is None else min(abs(requested), max(0, annual_cap - used))
        trade = -permitted if requested < 0 else permitted
        cap_limited = not isclose(permitted, abs(requested), abs_tol=1e-12)
        turnover = abs(trade)
        equity = min(1.0, max(0.0, equity + trade))
        used += turnover
        gross_factor = equity * (1 + row.equity_return) + (1 - equity) * (1 + row.bill_return)
        gross = gross_factor - 1
        yield Outcome(row.month, equity, gross, gross - cost * turnover,
                      turnover, target, cap_limited, row.decision_date)
        equity *= (1 + row.equity_return) / gross_factor


def summarize(outcomes):
    months = list(outcomes)
    if not months:
        raise ValueError("Cannot summarize an empty period.")
    equity = 1.0
    peak = 1.0
    drawdown = 0.0
    for row in months:
        equity *= 1 + row.net_return
        peak = max(peak, equity)
        drawdown = max(drawdown, 1 - equity / peak)
    return {
        "gross": prod(1 + x.gross_return for x in months) - 1,
        "net": equity - 1,
        "switches": sum(x.turnover > 1e-12 for x in months),
        "turnover": sum(x.turnover for x in months),
        "max_drawdown": drawdown,
        "worst_month": min(x.net_return for x in months),
        "average_equity": sum(x.equity_weight for x in months) / len(months),
        "cap_limited_months": sum(x.cap_limited for x in months),
    }


# The authored Lab 18 training fixture. Percent units as printed in the course.
TRAINING = [
    ("2024-12", 0.8, None),
    ("2025-01", 1.2, 2.0), ("2025-02", 0.9, 1.5), ("2025-03", 1.5, 3.0),
    ("2025-04", -1.0, -2.5), ("2025-05", -0.7, -1.5), ("2025-06", -1.4, -3.0),
    ("2025-07", 1.1, 2.5), ("2025-08", 0.6, 1.0), ("2025-09", 0.9, 2.0),
    ("2025-10", -0.9, -2.0), ("2025-11", -0.5, -1.0), ("2025-12", 1.6, 3.5),
    ("2026-01", -1.1, -2.0), ("2026-02", 0.7, 1.5), ("2026-03", -1.3, -3.0),
    ("2026-04", 0.8, 2.0), ("2026-05", -0.6, -1.5), ("2026-06", 0.5, 1.0),
]


def training_results(lag=1):
    if lag not in (0, 1):
        raise ValueError("The training fixture supports lag 0 or 1.")
    months = [Month(month, .003, equity / 100, TRAINING[i - lag][1])
              for i, (month, _, equity) in enumerate(TRAINING) if equity is not None]
    rule = list(simulate(months, lambda s: float(s > 0), initial_equity=0, cost=.001))
    placebo = list(simulate(months, lambda s: float(s < 0), initial_equity=0, cost=.001))
    benchmark = list(simulate(months, lambda _: None, initial_equity=1, cost=0))
    return {label: {"rule": summarize(rule[window]), "placebo": summarize(placebo[window]),
                    "benchmark": summarize(benchmark[window])}
            for label, window in [("Development", slice(None, 12)), ("Holdout", slice(12, None))]}


def verify_training():
    results = training_results()
    expected = {
        "Development": ("6.55%", "6.13%", "2.16%", "5.33%", 4),
        "Holdout": ("-5.52%", "-6.09%", "4.88%", "-2.09%", 6),
    }
    for label, values in results.items():
        rule, placebo, benchmark = (values[key] for key in ("rule", "placebo", "benchmark"))
        actual = (f"{rule['gross']:.2%}", f"{rule['net']:.2%}", f"{placebo['net']:.2%}",
                  f"{benchmark['net']:.2%}", rule["switches"])
        if actual != expected[label]:
            raise AssertionError(f"{label}: expected {expected[label]}, got {actual}")
        print(label, *actual, sep=" | ")
    leak = training_results(lag=0)["Development"]["rule"]["net"]
    if f"{leak:.2%}" != "17.72%":
        raise AssertionError(f"Lag-zero control: expected 17.72%, got {leak:.2%}")
    print(f"Lag-zero leakage control | {leak:.2%}")


if __name__ == "__main__":
    verify_training()
