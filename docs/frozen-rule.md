# FEDFUNDS overlay — frozen rule v1

The student selected a 10-percentage-point defensive move to reduce equity exposure during tightening while retaining a modeled return above the provisional 6.5% screen. Lab 15 static estimates were 6.91% return and 6.04% volatility for 60% BIL / 40% VT. The higher-BIL proposal was dropped before a strategy run because it fell short of the screen.

| Item | Locked primary specification |
| --- | --- |
| Neutral and initial position | 50% BIL / 50% VT. |
| Rate trigger | Latest available monthly FEDFUNDS less the value three calendar observation months earlier, both from the same ALFRED vintage. At or above +0.25 percentage points, target 60% BIL / 40% VT. Otherwise target 50/50. |
| Timing | Use the latest archived vintage dated no later than one calendar day before the prior month's last common trading session. Trade at that session's close for the following monthly holding period. If the rate pair is unavailable, retain drifted holdings. |
| Comparisons | Fixed 50/50 under the same rebalancing, turnover and cost mechanics. Flipped-signal check uses the same defensive weights at or below −0.25 points. Report VT buy-and-hold as context. |
| Turnover and costs | 25% one-way turnover per trade calendar year, measured from drifted weights. Reduce any requested trade to the remaining budget. Subtract 10 basis points per 100% turnover from monthly gross return. |
| Periods | Development October 2021 through September 2025. Historical outcome holdout October 2025 through September 2026. Carry positions and remaining turnover from development into holdout. The ETF returns were previously used in Lab 15; the rule was not evaluated on them before this freeze. |
| Decision | Reject if holdout net return trails the fixed allocation or flipped signal, or if monthly-close net drawdown is worse than fixed 50/50. If otherwise passing, classify fewer than two defensive requests or an unchanged position path as inconclusive. Other passes support a restricted research pilot subject to mandate checks, committee approval, and prospective evidence. |

The 55% BIL / 45% VT alternative belongs to a later committee review if refreshed estimates put the 60/40 target below 6.5%. It is outside the primary test. The rule uses only observed FEDFUNDS. Rate expectations, balance-sheet changes, and earnings are separate hypotheses or monitoring context. Monthly trading is a research exception to the annual rebalancing policy.

The pre-run [data record](../data/input_manifest.json) identifies the source and locks the normalized CSV inputs. See [data provenance](data-provenance.md) for the price and release alignment.
