# Project 2 verification before the project holdout

The course training fixture is separate from the ETF project. Reproduce these computed results with `python backtest.py`.

| Course period | Rule gross | Rule net | Flipped rule net | Equity buy-and-hold reference | Rule switches |
| --- | ---: | ---: | ---: | ---: | ---: |
| Development | 6.55% | 6.13% | 2.16% | 5.33% | 4 |
| Holdout | −5.52% | −6.09% | 4.88% | −2.09% | 6 |

The lag-zero leakage control gives 17.72% development net. That is the intentionally invalid training control. The course rounds the net calculations using monthly gross return less cost per switch. Deducting the cost as a separate wealth multiplier did not reproduce the placebo and leakage values. The shared engine uses the monthly return convention and charges the project trade cost on one-way turnover.

Other checks completed before running the project signal:

- **Mandate UI.** The bundled ETF optimal allocation reproduced 6.91% estimate, 6.04% volatility and 60% eligible reserve. The reserve verdict passed on that proposal and failed on the policy reference. Five-day liquidity remained unresolved. The 36-month controls gave 6.75% estimate, 1.79% volatility and 85% reserve. The Meridian screen still gave 6.51% and 9.44%.
- **Archived source.** The Lab 17 FEDFUNDS snapshot requested on October 31, 2026 exposed a September observation of 3.75% and a June observation of 3.63%. Passing an earlier cutoff than the file's effective vintage was rejected. This was an AI-run parser check, separate from the student's independent verification.
- **Trading mechanics.** A synthetic 10-point shift charged 1 basis point at a 10 basis point full-turnover assumption. A December trade followed by January returns used the December calendar-year budget. A later January trade used the reset budget. A synthetic missing-signal case did not count as evidence for a pilot.

**Pending:** student rule review, verified decision dates and data manifest, pre-run commit and push, ETF holdout, and student-authored validation.
