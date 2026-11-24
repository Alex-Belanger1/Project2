"""Streamlit interface for the Project 2 portfolio and mandate screens."""

import json
from copy import deepcopy
from pathlib import Path

import streamlit as st

from mandate_checks import allocation_checks
from sensitivity import development_sensitivity
from signal_test import DEFENSIVE_EQUITY, NEUTRAL_EQUITY, REVIEW_FALLBACK_EQUITY
from portfolio import (
    CORRELATIONS,
    DEFAULT_RESERVE_MINIMUM,
    OBJECTIVE_RETURN,
    SLEEVES,
    covariance_matrix,
    equal_weight_portfolio,
    estimate_from_prices,
    expected_return,
    find_lowest_risk_mix,
    inverse_volatility_portfolio,
    portfolio_volatility,
    reserve_eligible_weight,
)


st.set_page_config(page_title="Meridian Foundation Reserve", layout="wide")
st.title("Meridian Foundation Reserve")
st.caption("Built with AI help, a learning demonstration, not investment advice.")


def reset_base():
    """Restore the reference scenario and all editable controls."""
    keys = {"source", "objective", "reserve_minimum", "recent_window", "lag", "cost_bp"}
    for key in list(st.session_state):
        if key in keys or key.startswith(("return_", "eligibility_")):
            del st.session_state[key]


st.sidebar.header("Mandate and data")
st.sidebar.button("Reset to base", on_click=reset_base)
source = st.sidebar.radio("Price inputs", ["Project ETFs", "Meridian training"], key="source")
objective = st.sidebar.number_input(
    "Annual return objective (%)", min_value=-25.0, max_value=50.0,
    value=OBJECTIVE_RETURN * 100, step=0.1, key="objective",
) / 100
reserve_minimum = st.sidebar.number_input(
    "Reserve-eligible minimum (%)", min_value=0.0, max_value=100.0,
    value=DEFAULT_RESERVE_MINIMUM * 100, step=1.0, key="reserve_minimum",
) / 100
if source == "Project ETFs":
    price_file = Path(__file__).resolve().parent / "data" / "verified_prices.csv"
else:
    price_file = None
last_36_months = st.sidebar.toggle("Use last 36 monthly returns", value=False, key="recent_window")


def with_reserve_choices(sleeves, prefix):
    """Return a copy of sleeves with the page's reserve-eligibility choices."""
    selected = deepcopy(sleeves)
    for name in selected:
        selected[name]["reserve_eligible"] = st.checkbox(
            f"Reserve eligible — {name}",
            value=selected[name]["reserve_eligible"],
            key=f"eligibility_{prefix}_{name}",
        )
    return selected


def show_result(label, result):
    """Display one engine result without recalculating portfolio math in the app."""
    st.subheader(label)
    if result is None:
        st.warning("No mix meets the objective and reserve rule.")
        return
    st.table([{"Asset": name, "Weight (%)": f"{weight * 100:.2f}"} for name, weight in result["weights"].items()])
    first, second, third = st.columns(3)
    first.metric("Expected return estimate", f"{result['return'] * 100:.2f}%")
    second.metric("Volatility", f"{result['volatility'] * 100:.2f}%")
    third.metric("Reserve eligible", f"{result['reserve_weight'] * 100:.2f}%")


try:
    if price_file is None:
        loaded_sleeves, loaded_correlations = deepcopy(SLEEVES), deepcopy(CORRELATIONS)
        data_label = "Meridian training inputs"
    else:
        loaded_sleeves, loaded_correlations = estimate_from_prices(price_file, False)
        data_label = f"{source} — all monthly returns"

    if price_file is not None and last_36_months:
        active_sleeves, active_correlations = estimate_from_prices(price_file, True)
        data_label = f"{source} — last 36 monthly returns"
    else:
        active_sleeves, active_correlations = deepcopy(loaded_sleeves), deepcopy(loaded_correlations)
except ValueError as error:
    st.error(f"Could not estimate from prices.csv: {error}")
    st.stop()

if source == "Project ETFs":
    for name in ("BIL", "IEF"):
        active_sleeves[name]["reserve_eligible"] = True
        loaded_sleeves[name]["reserve_eligible"] = True

st.write(f"Active inputs: **{data_label}**. Edit estimated returns and reserve eligibility below.")
for name, data in active_sleeves.items():
    data["return"] = st.number_input(
        f"Expected return estimate — {name} (%)", min_value=-100.0, max_value=100.0,
        value=float(data["return"] * 100), step=0.1, key=f"return_{data_label}_{name}",
    ) / 100
active_sleeves = with_reserve_choices(active_sleeves, source)

loaded_result = find_lowest_risk_mix(
    loaded_sleeves, loaded_correlations, OBJECTIVE_RETURN, DEFAULT_RESERVE_MINIMUM
)
active_result = find_lowest_risk_mix(
    active_sleeves, active_correlations, objective, reserve_minimum
)

left, right = st.columns(2)
with left:
    show_result("Lowest-risk mix for current controls", active_result)
with right:
    show_result("Base scenario", loaded_result)
    st.caption("Original estimates, 6.5% return target, 3% reserve floor, and default eligibility.")

if active_result is not None and loaded_result is not None:
    largest_change = max(
        abs(active_result["weights"][name] - loaded_result["weights"][name])
        for name in active_result["weights"]
    )
    st.info(f"Largest weight change from base: **{largest_change * 100:.0f} points**.")
else:
    st.info("Largest weight change is unavailable because one of the two searches has no feasible mix.")

st.header("Baselines and mandate verdicts")
st.caption(
    "The search uses the selected reserve assumptions and a historical nominal return estimate. "
    "The verdicts flag unapproved reserve classifications and other rules requiring committee evidence."
)
portfolios = {
    "Equal weight": equal_weight_portfolio(active_sleeves),
    "Inverse volatility": inverse_volatility_portfolio(active_sleeves),
}
policy_universe = set(active_sleeves) == {"BIL", "IEF", "LQD", "VT"}
if policy_universe:
    portfolios["Policy reference"] = {"BIL": 0, "IEF": 0, "LQD": .4, "VT": .6}
    for label, equity_weight in (
        ("Fixed 50/50", NEUTRAL_EQUITY),
        ("Defensive target", DEFENSIVE_EQUITY),
        ("Committee fallback", REVIEW_FALLBACK_EQUITY),
    ):
        portfolios[label] = {"BIL": 1 - equity_weight, "IEF": 0, "LQD": 0, "VT": equity_weight}
if active_result is not None:
    portfolios["Minimum volatility"] = active_result["weights"]

covariance = covariance_matrix(active_sleeves, active_correlations)
summary_rows = []
verdict_rows = []
for name, weights in portfolios.items():
    summary_rows.append({
        "Portfolio": name,
        **{ticker: f"{weight:.2%}" for ticker, weight in weights.items()},
        "Return estimate": f"{expected_return(weights, active_sleeves):.2%}",
        "Volatility estimate": f"{portfolio_volatility(weights, covariance):.2%}",
        "Eligible reserve": f"{reserve_eligible_weight(weights, active_sleeves):.2%}",
    })
    for verdict in allocation_checks(
        weights, active_sleeves, objective, reserve_minimum, policy_universe=policy_universe
    ):
        verdict_rows.append({"Portfolio": name, "Rule": verdict.rule,
                             "Verdict": verdict.status, "Evidence": verdict.evidence})
st.dataframe(summary_rows, hide_index=True)
st.dataframe(verdict_rows, hide_index=True)
if policy_universe:
    st.caption(
        "If the defensive target falls below the return screen, consider the fallback only "
        "if it clears the screen and the reserve and turnover rules permit the move. "
        "This is a committee review, separate from the historical backtest."
    )

st.header("Frozen FEDFUNDS holdout")
result_file = Path(__file__).resolve().parent / "output" / "holdout.json"
if result_file.is_file():
    with result_file.open(encoding="utf-8") as handle:
        evidence = json.load(handle)
    st.caption(f"Historical holdout {evidence['holdout']}. The portfolio controls above use separate estimates.")
    st.subheader(evidence["decision"] + " the tactical overlay" if evidence["decision"] == "Reject"
                 else evidence["decision"])
    st.write(". ".join(reason.capitalize() for reason in evidence["reasons"]) + ".")
    holdout_rows = []
    for name, periods in evidence["results"].items():
        result = periods["holdout"]
        holdout_rows.append({
            "Strategy": name, "Gross": f"{result['gross']:.2%}", "Net": f"{result['net']:.2%}",
            "Max drawdown": f"{result['max_drawdown']:.2%}",
            "Defensive requests": result["defensive_requests"],
        })
    st.dataframe(holdout_rows, hide_index=True)
else:
    st.info("Run `python evaluate.py --write` to generate the frozen result.")

st.header("Development sensitivity")
st.caption("October 2021–September 2025 only. These controls leave the frozen holdout unchanged.")
lag_control, cost_control = st.columns(2)
lag = lag_control.selectbox("Signal cutoff before trade (calendar days)", [1, 7], key="lag")
cost_bp = cost_control.slider("Trading cost (bp per 100% one-way turnover)", 0, 50, 10, key="cost_bp")
try:
    sensitivity = development_sensitivity(lag, cost_bp)
except (OSError, ValueError) as error:
    st.error(f"Development data could not be verified: {error}")
else:
    st.dataframe([
        {"Strategy": name, "Gross": f"{row['gross']:.2%}", "Net": f"{row['net']:.2%}",
         "Max drawdown": f"{row['max_drawdown']:.2%}", "Turnover": f"{row['turnover']:.2%}",
         "Defensive requests": row["defensive_requests"]}
        for name, row in sensitivity.items()
    ], hide_index=True)
