# Portfolio screen — visible output

As of September 2026. Monthly adjusted-close estimates, four USD ETFs, long-only 5-point grid. The default hurdle is 6.5% nominal and the eligible-reserve floor is 3%. BIL and IEF count for the modeled reserve screen; IEF eligibility needs approval.

| Scenario | BIL / IEF / LQD / VT | Est. annual return | Est. annual volatility | Modeled result |
| --- | --- | ---: | ---: | --- |
| Equal weight | 25 / 25 / 25 / 25 | 3.22% | 7.50% | Fails return screen |
| Inverse volatility | 86.81 / 5.75 / 4.49 / 2.95 | 3.33% | 1.40% | Fails return screen |
| Full window, minimum volatility | 60 / 0 / 0 / 40 | 6.91% | 6.04% | Passes modeled return and reserve screens |
| 36-month window | 85 / 0 / 0 / 15 | 6.75% | 1.79% | Passes modeled screens; 25-point maximum weight change |
| VT estimate lower by 1 percentage point | 60 / 0 / 0 / 40 | 6.51% | 6.04% | Keeps the mix; only about 0.01 points above hurdle |
| 70% reserve minimum | — | — | — | No feasible mix |
| 7.2% return target | 55 / 0 / 0 / 45 | 7.33% | 6.78% | Passes modeled screens |

The portfolio screen supports a research shortlist. Liquidity, issuer exposure, suitability and applicable governance approvals remain unresolved for implementation. [Separate FEDFUNDS decision and holdout](holdout.md).

## One-at-a-time driver ranking

Each row changes one assumption from the full-sample 6.5% return / 3% reserve base. The feasible scenarios are ordered by the largest absolute change in any one portfolio weight. This ranking applies to these specific shocks. The 70% reserve scenario is a boundary test and is listed separately because it removes feasibility.

| Rank | Driver and test | Largest weight change | Committee implication |
| --- | --- | ---: | --- |
| Boundary | Reserve floor from 3% to 70% | — | No feasible mix. Review mandate or inputs before allocating. |
| 1 | Use 36 instead of 60 monthly returns | 25 points | Refresh and challenge the estimation window before relying on the base weights. |
| 2 | Raise the annual return target from 6.5% to 7.2% | 5 points | The original mix fails; 55% BIL / 45% VT is the new screening candidate. |
| 3 | Reduce estimated annual VT return by 1 point | 0 points | The allocation stays the same but its modeled return falls to 6.51%, almost at the hurdle. |

Lag and cost belong to the separate backtest. Over development only, widening the publication buffer from one day to seven moves net return by **0.000 points**. Raising the one-way turnover cost from 10 to 25 bp reduces net return by **0.113 points**. The two comparisons use the same development months and leave the holdout fixed. [Method and inputs](../docs/validation-and-ai-use.md).
