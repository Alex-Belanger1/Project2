"""Evidence-based mandate screens for the portfolio application."""

from dataclasses import dataclass
from math import isclose, isfinite

from portfolio import expected_return, reserve_eligible_weight


@dataclass(frozen=True)
class Verdict:
    rule: str
    status: str
    evidence: str


def check(rule, passes, evidence):
    return Verdict(rule, "Unresolved" if passes is None else "Pass" if passes else "Fail", evidence)


def allocation_checks(weights, sleeves, objective, reserve_minimum, *, policy_universe):
    """Evaluate a static proposal. Missing policy or holdings evidence stays unresolved."""
    total = sum(weights.values())
    valid = set(weights) == set(sleeves) and all(isfinite(w) for w in weights.values())
    fully_invested = valid and isclose(total, 1.0, abs_tol=1e-9, rel_tol=0)
    long_only = valid and all(0 <= w <= 1 for w in weights.values())
    checks = [
        check("Weights and funding", fully_invested, f"Weights total {total:.2%}."),
        check("Long only and no leverage", long_only and fully_invested,
              "Direct position weights must be between 0% and 100%."),
    ]
    if valid:
        ret = expected_return(weights, sleeves)
        reserve = reserve_eligible_weight(weights, sleeves)
        checks.extend([
            check("Nominal return estimate screen", ret + 1e-12 >= objective,
                  f"{ret:.2%} estimated versus {objective:.2%} screen."),
            check("Eligible reserve screen", reserve + 1e-12 >= reserve_minimum,
                  f"{reserve:.2%} eligible versus {reserve_minimum:.2%} floor."),
        ])
    else:
        checks.extend([
            check("Nominal return estimate screen", None, "Invalid weight inputs."),
            check("Eligible reserve screen", None, "Invalid weight inputs."),
        ])
    if not policy_universe:
        return checks
    checks.extend([
        check("Approved vehicle universe", valid and all(
            weight == 0 or ticker in {"BIL", "IEF", "LQD", "VT"}
            for ticker, weight in weights.items()), "Direct positions are limited to the four ETF candidates."),
        check("Derivatives restriction", None, "No direct derivatives are modeled. Fund-level eligibility needs review."),
        check("Reserve vehicle eligibility", None if valid and weights.get("IEF", 0) > 0
              and sleeves["IEF"]["reserve_eligible"] else True,
              "IEF needs approval before counting toward the reserve. The screen uses selected eligibility."),
        check("Five-day liquidity", None, "Need trade-size and execution evidence for the 90% liquidity rule."),
        check("8% single-issuer limit", None, "Need underlying holdings and the approved exemption policy."),
        check("25% annual turnover", None, "Static allocations do not establish realized turnover."),
        check("Rebalance authority", None, "Monthly tactical trading requires a committee exception."),
        check("Calendar-year loss rule (S9)", None, "Committee must define the loss measure and breach response."),
        check("CPI + 4% net over rolling five years", None, "A historical nominal estimate does not establish this outcome."),
    ])
    return checks
