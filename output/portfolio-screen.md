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
