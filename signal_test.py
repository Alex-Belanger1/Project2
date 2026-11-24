"""Align verified vintages with next-month ETF returns and compare fixed rules."""

import csv
import re
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from io import StringIO
from math import isfinite
from pathlib import Path

from backtest import Month, simulate, summarize

NEUTRAL_EQUITY = .50
DEFENSIVE_EQUITY = .40
REVIEW_FALLBACK_EQUITY = .45


@dataclass(frozen=True)
class RateEvidence:
    requested_as_of: date
    effective_vintage: date
    latest_month: date
    latest_value: Decimal
    prior_month: date
    prior_value: Decimal

    @property
    def change(self):
        return self.latest_value - self.prior_value


def shift_month(day, months):
    index = day.year * 12 + day.month - 1 + months
    year, month = divmod(index, 12)
    return date(year, month + 1, 1)


def parse_vintage(text, as_of, change_months=3):
    """Accept only an ALFRED FEDFUNDS vintage that existed by the cutoff."""
    reader = csv.DictReader(StringIO(text.lstrip("\ufeff")))
    fields = reader.fieldnames or []
    match = re.fullmatch(r"FEDFUNDS_(\d{8})", fields[1]) if len(fields) == 2 else None
    if not match or fields[0] != "observation_date":
        raise ValueError("Expected an ALFRED FEDFUNDS vintage header.")
    year, month, day = match[1][:4], match[1][4:6], match[1][6:]
    effective = date.fromisoformat(f"{year}-{month}-{day}")
    if effective > as_of:
        raise ValueError("ALFRED vintage falls after the decision cutoff.")
    rates = {}
    for row in reader:
        value = row[fields[1]]
        if value in ("", ".", None):
            continue
        observation = date.fromisoformat(row["observation_date"])
        if observation.day != 1 or shift_month(observation, 1) > effective:
            raise ValueError("ALFRED vintage includes an incomplete observation month.")
        if observation in rates:
            raise ValueError("Duplicate observation month in ALFRED vintage.")
        try:
            rate = Decimal(value)
        except InvalidOperation as exc:
            raise ValueError("Invalid FEDFUNDS value.") from exc
        if not rate.is_finite():
            raise ValueError("FEDFUNDS value must be finite.")
        rates[observation] = rate
    if not rates:
        return None
    latest = max(rates)
    prior = shift_month(latest, -change_months)
    if prior not in rates:
        return None
    return RateEvidence(as_of, effective, latest, rates[latest], prior, rates[prior])


def read_months(prices_path, sessions, vintage_text, *, start, end, lag_days=1):
    """Build requested return months using previous month's last session.

    sessions maps YYYY-MM to a verified exchange close date.
    vintage_text accepts a cutoff date and returns archived CSV text or None.
    """
    if lag_days < 1:
        raise ValueError("At least one calendar day of timing buffer is required.")
    months, audit = [], []
    with Path(prices_path).open(encoding="utf-8-sig", newline="") as handle:
        rows = csv.DictReader(handle)
        previous = None
        for row in rows:
            period = date.fromisoformat(row["Date"])
            if period.day != 1:
                raise ValueError("Monthly prices must be labeled on the first day.")
            label = period.isoformat()[:7]
            if label > end:
                break
            if previous is not None and period != shift_month(previous[0], 1):
                raise ValueError("Monthly prices must be ordered and consecutive.")
            bill = float(row["BIL"])
            equity = float(row["VT"])
            if not all(isfinite(price) and price > 0 for price in (bill, equity)):
                raise ValueError("Prices must be finite and positive.")
            if label >= start and previous is not None:
                decision_month = previous[0].isoformat()[:7]
                decision = sessions[decision_month]
                if decision.isoformat()[:7] != decision_month:
                    raise ValueError("Decision close does not belong to the prior month.")
                cutoff = decision - timedelta(days=lag_days)
                text = vintage_text(cutoff)
                evidence = parse_vintage(text, cutoff) if text is not None else None
                audit.append((label, decision, cutoff, evidence))
                months.append(Month(label, bill / previous[1] - 1, equity / previous[2] - 1,
                                    float(evidence.change) if evidence else None, decision))
            previous = (period, bill, equity)
    if not months or months[0].month != start or months[-1].month != end:
        raise ValueError("Price file does not cover the requested months and starting close.")
    return months, audit


def simulate_rules(months, *, cost=.001, annual_cap=.25,
                   threshold=.25, neutral_equity=NEUTRAL_EQUITY, defensive_equity=DEFENSIVE_EQUITY):
    """Run identical trading and cost mechanics across the fixed mix and two overlays."""
    def tactical(signal, sign):
        if signal is None:
            return None
        return defensive_equity if sign * signal >= threshold else neutral_equity

    months = tuple(months)
    if threshold <= 0 or not 0 <= defensive_equity < neutral_equity <= 1:
        raise ValueError("Use a positive trigger and a defensive equity weight below neutral.")
    rules = {
        "FEDFUNDS overlay": lambda s: tactical(s, 1),
        "Flipped signal": lambda s: tactical(s, -1),
        "Fixed 50/50": lambda _: neutral_equity,
    }
    series = {name: list(simulate(months, rule, initial_equity=neutral_equity,
                                  cost=cost, annual_cap=annual_cap))
              for name, rule in rules.items()}
    series["VT buy-and-hold reference"] = list(simulate(
        months, lambda _: None, initial_equity=1, cost=0
    ))
    return series


def compare(months, *, holdout_start, cost=.001, annual_cap=.25,
            threshold=.25, neutral_equity=NEUTRAL_EQUITY, defensive_equity=DEFENSIVE_EQUITY):
    """Report the frozen rule as separate development and holdout periods."""
    series = simulate_rules(months, cost=cost, annual_cap=annual_cap, threshold=threshold,
                            neutral_equity=neutral_equity, defensive_equity=defensive_equity)
    results = {}
    for name, rows in series.items():
        results[name] = {
            "development": summarize(row for row in rows if row.month < holdout_start),
            "holdout": summarize(row for row in rows if row.month >= holdout_start),
        }
        for period, test in [("development", lambda m: m < holdout_start),
                             ("holdout", lambda m: m >= holdout_start)]:
            results[name][period]["defensive_requests"] = sum(
                row.target == defensive_equity for row in rows if test(row.month)
            )
    return results, series


def decision(results, series, holdout_start):
    overlay = results["FEDFUNDS overlay"]["holdout"]
    neutral = results["Fixed 50/50"]["holdout"]
    placebo = results["Flipped signal"]["holdout"]
    failures = []
    if overlay["net"] < neutral["net"] - 1e-12:
        failures.append("net return trailed the fixed comparison")
    if overlay["net"] < placebo["net"] - 1e-12:
        failures.append("net return trailed the flipped signal")
    if overlay["max_drawdown"] > neutral["max_drawdown"] + 1e-12:
        failures.append("monthly-close drawdown worsened")
    if failures:
        return "Reject", failures
    differs = any(abs(a.equity_weight - b.equity_weight) > 1e-12
                  for a, b in zip(series["FEDFUNDS overlay"], series["Fixed 50/50"])
                  if a.month >= holdout_start)
    if overlay["defensive_requests"] < 2 or not differs:
        return "Inconclusive", ["too little defensive exposure to assess the rule"]
    return "Research pilot only", ["historical gates passed; prospective evidence and approval required"]
