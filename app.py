"""Streamlit interface for the Project 2 portfolio and mandate screens."""

from copy import deepcopy
from pathlib import Path

import streamlit as st

from mandate_checks import allocation_checks
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

st.sidebar.header("Mandate and data")
source = st.sidebar.radio("Price inputs", ["Project ETFs", "Meridian training", "Upload CSV"])
objective = st.sidebar.number_input(
    "Annual return objective (%)", min_value=-25.0, max_value=50.0,
    value=OBJECTIVE_RETURN * 100, step=0.1,
) / 100
reserve_minimum = st.sidebar.number_input(
    "Reserve-eligible minimum (%)", min_value=0.0, max_value=100.0,
    value=DEFAULT_RESERVE_MINIMUM * 100, step=1.0,
) / 100
if source == "Upload CSV":
    price_file = st.sidebar.file_uploader(
        "Upload prices.csv", type="csv", help="Date first, oldest first, and one adjusted-close column per ticker."
    )
    if price_file is None:
        st.info("Upload a monthly adjusted-close CSV to continue.")
        st.stop()
elif source == "Project ETFs":
    price_file = Path(__file__).resolve().parent / "data" / "verified_prices.csv"
else:
    price_file = None
last_36_months = st.sidebar.toggle("Use last 36 monthly returns", value=False)


def with_reserve_choices(sleeves, prefix):
    """Return a copy of sleeves with the page's reserve-eligibility choices."""
    selected = deepcopy(sleeves)
    for name in selected:
        selected[name]["reserve_eligible"] = st.checkbox(
            f"Reserve eligible — {name}",
            value=selected[name]["reserve_eligible"],
            key=f"{prefix}_reserve_{name}",
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

st.write(f"Active inputs: **{data_label}**. Edit estimated returns and reserve eligibility below.")
for name, data in active_sleeves.items():
    data["return"] = st.number_input(
        f"Expected return estimate — {name} (%)", min_value=-100.0, max_value=100.0,
        value=float(data["return"] * 100), step=0.1, key=f"return_{data_label}_{name}",
    ) / 100
active_sleeves = with_reserve_choices(active_sleeves, source)

# Compare original estimates using the current mandate and reserve selections.
for name in loaded_sleeves:
    loaded_sleeves[name]["reserve_eligible"] = active_sleeves[name]["reserve_eligible"]
loaded_result = find_lowest_risk_mix(
    loaded_sleeves, loaded_correlations, objective, reserve_minimum
)
active_result = find_lowest_risk_mix(
    active_sleeves, active_correlations, objective, reserve_minimum
)

left, right = st.columns(2)
with left:
    show_result("Lowest-risk mix for current controls", active_result)
with right:
    show_result("Answer for inputs as loaded", loaded_result)
    st.caption("Uses the original estimates and the current mandate and reserve selections.")

if active_result is not None and loaded_result is not None:
    largest_change = max(
        abs(active_result["weights"][name] - loaded_result["weights"][name])
        for name in active_result["weights"]
    )
    st.info(f"Largest weight change from the loaded answer: **{largest_change * 100:.0f} points**.")
else:
    st.info("Largest weight change is unavailable because one of the two searches has no feasible mix.")

st.header("Baselines and mandate verdicts")
st.caption("The return hurdle uses a historical nominal estimate. Unresolved rules still need committee evidence.")
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
