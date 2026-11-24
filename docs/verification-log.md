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

## Project rule freeze and evaluation

The student chose the 60% BIL / 40% VT defensive target. The [rule and locked inputs were pushed to GitHub](https://github.com/Alex-Belanger1/Project2/commit/4852c5eb2062a4bce2f92ba2de5b80c2eb055a7e) before the primary evaluation. The remote branch SHA was checked directly before running the evaluation.

The [holdout](../output/holdout.md) activated the observed-rate trigger zero times. Its 10.08% net result and 2.97% monthly-close drawdown matched fixed 50/50. The flipped comparison returned 10.38% net with a 2.32% drawdown. The pre-specified relative-return gate therefore rejects the tactical overlay. Zero triggers also mean that this holdout provides no active test of downside protection from the observed tightening rule. The development segment did activate the rule and is separate evidence.

## Student changed-input record

The student's original prediction was committed before changing the return target. The [comparison](changed-input-result.md) records the exact input change, expected direction, actual effect, and committee implication.

## Student independent check of AI output

The student independently checked the [ALFRED vintage requested September 29, 2025](https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=FEDFUNDS&vintage_date=2025-09-29), the cutoff used for the September 30 trade and the October 2025 holding period.

> the most recent data point is 8/1/2025 and 4.33, the rate 3 observations months earlier is on 5/1/2025 and is still 4.33 so it doesnt meet the .25 percentage point trigger

The source values imply a **0.00 percentage-point** change. The student's finding matched the [frozen inputs](../data/alfred/2025-09-29.csv) and the computed historical decision to target **50% BIL / 50% VT** for October. The independent check confirmed the observation dates, units, and absence of an activation in the first holdout month. No correction was needed for this check.

**Pending:** final memo, recorded videos, and submission review.
