"""Calculate, estimate, and search long-only portfolio mixes for Lab 15."""

import csv
from datetime import datetime
from io import StringIO
from math import sqrt
from pathlib import Path
from statistics import mean, stdev


# Editable course-authored training inputs. Values are decimals, not percentages.
SLEEVES = {
    "Treasury bills": {"return": 0.035, "volatility": 0.005, "reserve_eligible": True},
    "Treasury 10-year note": {"return": 0.043, "volatility": 0.070, "reserve_eligible": True},
    "Investment-grade bond fund": {"return": 0.050, "volatility": 0.060, "reserve_eligible": False},
    "Global equity index fund": {"return": 0.080, "volatility": 0.160, "reserve_eligible": False},
}

CORRELATIONS = {
    "Treasury bills": {
        "Treasury bills": 1.00, "Treasury 10-year note": 0.10,
        "Investment-grade bond fund": 0.05, "Global equity index fund": 0.00,
    },
    "Treasury 10-year note": {
        "Treasury bills": 0.10, "Treasury 10-year note": 1.00,
        "Investment-grade bond fund": 0.80, "Global equity index fund": -0.10,
    },
    "Investment-grade bond fund": {
        "Treasury bills": 0.05, "Treasury 10-year note": 0.80,
        "Investment-grade bond fund": 1.00, "Global equity index fund": 0.25,
    },
    "Global equity index fund": {
        "Treasury bills": 0.00, "Treasury 10-year note": -0.10,
        "Investment-grade bond fund": 0.25, "Global equity index fund": 1.00,
    },
}

OBJECTIVE_RETURN = 0.065
DEFAULT_RESERVE_MINIMUM = 0.03


def validate_correlations(correlations, sleeves):
    """Raise ValueError unless the full correlation table is symmetric and valid."""
    names = tuple(sleeves)
    if set(correlations) != set(names):
        raise ValueError("Correlation table must have one row for every sleeve.")
    for left in names:
        if set(correlations[left]) != set(names):
            raise ValueError(f"Correlation row for {left} must have every sleeve.")
        for right in names:
            value = correlations[left][right]
            if not -1 <= value <= 1:
                raise ValueError(f"Correlation for {left} and {right} must be between -1 and 1.")
            if value != correlations[right][left]:
                raise ValueError(f"Correlation table is not symmetric for {left} and {right}.")


def covariance_matrix(sleeves, correlations):
    """Return covariance entries: correlation times the two sleeve volatilities."""
    return {
        left: {
            right: correlations[left][right] * sleeves[left]["volatility"] * sleeves[right]["volatility"]
            for right in sleeves
        }
        for left in sleeves
    }


def expected_return(weights, sleeves):
    """Return the weighted expected return."""
    return sum(weights[name] * sleeves[name]["return"] for name in sleeves)


def portfolio_volatility(weights, covariance):
    """Return sqrt(w' covariance w), including each covariance term."""
    variance = sum(
        weights[left] * weights[right] * covariance[left][right]
        for left in weights
        for right in weights
    )
    if variance < -1e-12:
        raise ValueError("Portfolio variance is negative; check the input correlation table.")
    return sqrt(max(variance, 0))


def reserve_eligible_weight(weights, sleeves):
    """Return the combined weight of reserve-eligible sleeves."""
    return sum(weights[name] for name in sleeves if sleeves[name]["reserve_eligible"])


def _weight_vectors(names, step):
    """Yield every long-only weight vector that sums to one at the requested step."""
    units = round(1 / step)
    if units <= 0 or abs(units * step - 1) > 1e-9:
        raise ValueError("Step must divide 100% exactly (for example, 0.05).")

    def build(position, units_left, current):
        if position == len(names) - 1:
            yield dict(zip(names, [*current, units_left * step]))
            return
        for allocation in range(units_left + 1):
            yield from build(position + 1, units_left - allocation, [*current, allocation * step])

    yield from build(0, units, [])


def find_lowest_risk_mix(sleeves, correlations, objective, reserve_minimum, step=0.05):
    """Return the lowest-volatility feasible long-only mix, or None when none is feasible."""
    validate_correlations(correlations, sleeves)
    if not 0 <= reserve_minimum <= 1:
        raise ValueError("Reserve minimum must be between 0% and 100%.")
    covariance = covariance_matrix(sleeves, correlations)
    best = None
    for weights in _weight_vectors(tuple(sleeves), step):
        portfolio_return = expected_return(weights, sleeves)
        reserve_weight = reserve_eligible_weight(weights, sleeves)
        if portfolio_return + 1e-12 < objective or reserve_weight + 1e-12 < reserve_minimum:
            continue
        volatility = portfolio_volatility(weights, covariance)
        if best is None or volatility < best["volatility"] - 1e-12:
            best = {
                "weights": weights,
                "return": portfolio_return,
                "volatility": volatility,
                "reserve_weight": reserve_weight,
            }
    return best


def _csv_text(source):
    """Return UTF-8 CSV text from a path, an uploaded file, or a text stream."""
    if hasattr(source, "getvalue"):
        content = source.getvalue()
    elif hasattr(source, "read"):
        content = source.read()
    else:
        content = Path(source).read_bytes()
    if isinstance(content, bytes):
        return content.decode("utf-8-sig")
    return content


def estimate_from_prices(source, last_36_months=False):
    """Estimate annual return, volatility, and correlations from monthly adjusted-close prices.

    The input must have a Date column first, be oldest first, and have one numeric
    adjusted-close column per ticker. With ``last_36_months=True``, the estimate
    uses the last 36 monthly return observations (and therefore the last 37 prices).
    """
    reader = csv.DictReader(StringIO(_csv_text(source)))
    if not reader.fieldnames or reader.fieldnames[0] != "Date" or len(reader.fieldnames) < 3:
        raise ValueError("CSV must have Date first and at least two ticker columns.")
    tickers = reader.fieldnames[1:]
    rows = list(reader)
    if len(rows) < 3:
        raise ValueError("CSV needs at least three monthly price rows.")

    dates = []
    prices = {ticker: [] for ticker in tickers}
    for row_number, row in enumerate(rows, start=2):
        try:
            date = datetime.strptime(row["Date"], "%Y-%m-%d").date()
        except (TypeError, ValueError) as error:
            raise ValueError(f"Row {row_number} has an invalid Date; use YYYY-MM-DD.") from error
        dates.append(date)
        for ticker in tickers:
            try:
                price = float(row[ticker])
            except (TypeError, ValueError) as error:
                raise ValueError(f"Row {row_number} has an invalid {ticker} price.") from error
            if price <= 0:
                raise ValueError(f"Row {row_number} has a non-positive {ticker} price.")
            prices[ticker].append(price)
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise ValueError("Dates must be unique and ordered oldest first.")

    returns = {
        ticker: [current / previous - 1 for previous, current in zip(values, values[1:])]
        for ticker, values in prices.items()
    }
    if last_36_months:
        returns = {ticker: values[-36:] for ticker, values in returns.items()}
    observations = len(next(iter(returns.values())))
    if observations < 2:
        raise ValueError("CSV needs at least three prices (two monthly returns).")

    estimated_sleeves = {
        ticker: {
            "return": mean(values) * 12,
            "volatility": stdev(values) * sqrt(12),
            "reserve_eligible": False,
        }
        for ticker, values in returns.items()
    }
    correlations = {}
    for left in tickers:
        correlations[left] = {}
        for right in tickers:
            if left == right:
                correlations[left][right] = 1.0
                continue
            left_values, right_values = returns[left], returns[right]
            covariance = sum(
                (left_value - mean(left_values)) * (right_value - mean(right_values))
                for left_value, right_value in zip(left_values, right_values)
            ) / (observations - 1)
            denominator = stdev(left_values) * stdev(right_values)
            if denominator == 0:
                raise ValueError(f"Cannot calculate correlation: {left} or {right} has zero volatility.")
            correlations[left][right] = covariance / denominator
    return estimated_sleeves, correlations


def equal_weight_portfolio(sleeves):
    """Return equal weights across all sleeves."""
    return {name: 1 / len(sleeves) for name in sleeves}


def inverse_volatility_portfolio(sleeves):
    """Return weights proportional to the reciprocal of each sleeve's volatility."""
    inverse_volatilities = {name: 1 / data["volatility"] for name, data in sleeves.items()}
    total = sum(inverse_volatilities.values())
    return {name: value / total for name, value in inverse_volatilities.items()}


def baseline_portfolios(sleeves):
    """Define the three portfolios required by Lab 14."""
    benchmark = {name: 0.0 for name in sleeves}
    benchmark["Investment-grade bond fund"] = 0.40
    benchmark["Global equity index fund"] = 0.60
    return {
        "Benchmark": benchmark,
        "Equal weight": equal_weight_portfolio(sleeves),
        "Inverse volatility": inverse_volatility_portfolio(sleeves),
    }


def format_weights(weights):
    """Return the sleeve weights in the course-table order."""
    return " / ".join(f"{weights[name] * 100:.1f}" for name in SLEEVES)


def print_portfolio(name, weights, sleeves, covariance, objective):
    """Print one baseline's weights, expected return, risk, reserve share, and objective result."""
    portfolio_return = expected_return(weights, sleeves)
    volatility = portfolio_volatility(weights, covariance)
    reserve_weight = reserve_eligible_weight(weights, sleeves)
    meets_objective = "yes" if portfolio_return >= objective else "no"
    print(f"{name}:\n"
          f"  Weights (bills / 10-year / IG / equity): {format_weights(weights)}%\n"
          f"  Expected return: {portfolio_return * 100:.2f}%\n"
          f"  Volatility: {volatility * 100:.2f}%\n"
          f"  Reserve-eligible: {reserve_weight * 100:.1f}%\n"
          f"  Meets {objective * 100:.1f}% objective? {meets_objective}")


def main():
    """Validate inputs and print all baseline results."""
    validate_correlations(CORRELATIONS, SLEEVES)
    covariance = covariance_matrix(SLEEVES, CORRELATIONS)
    for name, weights in baseline_portfolios(SLEEVES).items():
        print_portfolio(name, weights, SLEEVES, covariance, OBJECTIVE_RETURN)
        print()


if __name__ == "__main__":
    main()
