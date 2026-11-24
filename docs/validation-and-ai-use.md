# Validation and AI use

**Decision.** Pilot the allocation screen for committee review and reject the observed FEDFUNDS overlay under the [pre-specified rule](frozen-rule.md). The holdout covers October 2025–September 2026. It evaluates a rule that had not been run on these returns before the freeze. The underlying price history had already been used for static estimates in Lab 15, so the holdout is historical, with no claim of prospective evidence.

| Requirement | Evidence |
| --- | --- |
| Reproducible inputs and timing | [Data card](data-provenance.md) and [locked input hashes](../data/input_manifest.json). Sixty dated ALFRED vintages were checked against their trade cutoffs. Wrong-series, future-vintage and incomplete-month checks guard against timing errors. A revision audit compared the 120 locked observations with the November 23, 2026 FRED download and found zero differences across 63 distinct observation months. The strategy uses only the dated vintages. |
| Known answers | `python backtest.py` reproduces the course gross/net results, the sign-flipped test and the lag-zero warning. Meridian's default minimum-volatility screen gives 6.51% estimated return and 9.44% volatility, with the known 0/20/25/55 weights. |
| Benchmarks and mandate | [Screens](../output/portfolio-screen.md) compare equal weight, inverse volatility and the constrained result. The app also displays the policy reference and its reserve failure. It distinguishes modeled rules from requirements that need committee evidence. |
| Holdout, placebo and costs | [Holdout output](../output/holdout.md). The 10 bp per 100% turnover assumption is charged symmetrically. The 25% cap is enforced by trade calendar year, even when the next month's return falls in January. |
| Important counterexample | A rate rule with zero holdout activations can look acceptable because the neutral portfolio did well. The trade ledger showed zero defensive requests and the same position path as fixed 50/50. The apparent tie does not establish protection. The flipped signal exceeded the overlay net, so the frozen rule rejects deployment. |
| Stability and costs | Window change shifted 25 points. A one-point lower VT estimate left the baseline at 6.51%, and a 70% reserve requirement produced no feasible mix. On development only, increasing cost from 10 to 25 bp reduced overlay net from 31.197% to 31.084%. Moving the cutoff buffer from one day to seven at 10 bp left development net at 31.197% and produced 18 defensive requests in both cases. The sensitivity runs leave the frozen holdout unchanged. |
| Student check of AI | The student independently retrieved September 29, 2025 ALFRED data: August and May were both 4.33%, so the 0.00-point change missed +0.25. The archived input and first holdout decision agreed. [Student's own words](verification-log.md#student-independent-check-of-ai-output). |
| Cold run | The [README](../README.md) provides the commands and limitations. See the [cold run record](cold-run.md) for the independent checkout checks. |

## Locked Changed-Input Record

The student's [verbatim AI-off prediction](changed-input-prediction.md) was committed at 19:39:24 Eastern on November 23, 2026 in `b8736fd36489a1d330d46a7ad0f84939d2019a70` before the changed case. Only the nominal annual return target changed, from 6.5% to 7.2%. The student predicted continued feasibility, higher volatility and return, and 80% equity.

The [actual result](changed-input-result.md) preserved feasibility but moved only five points into equity. Expected annual return increased from 6.91% to 7.33%; estimated volatility rose from 6.04% to 6.78%. The engine found that 45% VT was enough on the grid, so a larger equity allocation was unnecessary to meet the screen. This does not establish the behavior of realized drawdown. The candidate for committee review changes to 55% BIL / 45% VT if the higher hurdle is adopted. The signal decision stays reject.

## Signal selection ledger

| Candidate | Status | Rule, costs, and rationale |
| --- | --- | --- |
| Observed monthly FEDFUNDS, initial 10-point idea | Proposed | BIL/VT only. Three calendar observation months, +25 bp trigger, prior-day cutoff, 10 bp per full turnover. |
| Observed FEDFUNDS, 20-point student proposal | Dropped before running a strategy | The static 70% BIL / 30% VT target estimated 6.08%, below the 6.5% hurdle, and posed a larger turnover burden. A 65% BIL static target was also checked and fell just short before rounding. |
| 10-point observed-rate design | Frozen in [commit 4852c5e](https://github.com/Alex-Belanger1/Project2/commit/4852c5eb2062a4bce2f92ba2de5b80c2eb055a7e) | 50/50 neutral, 60% BIL / 40% VT in tightening, 25% annual cap. Ran the frozen historical evaluation. Rejected. |
| Flipped-rate signal and fixed 50/50 | Pre-specified controls | Same ETF pair, timing, cap and cost. The flipped signal uses a −25 bp threshold; fixed 50/50 never changes its target. VT buy-and-hold provides market context. |
| Seven-day cutoff and higher cost | Development sensitivity | Same allocation rule and universe. Seven-day dated vintages and a 25 bp trading cost were evaluated in development only. No holdout parameters were selected from their results. |
| Next-meeting hike expectations, yield curve, VT trend | Discussed only | No strategy runs. Futures expectations need separately timestamped evidence and an advance trigger definition. Earnings and Fed asset purchases remain monitoring context. |
| 55% BIL / 45% VT | Committee review option | Static fallback if refreshed estimates put 60/40 below the hurdle and the fallback clears mandate screens. Outside the frozen signal rule. |

## Material AI use

Codex (GPT-6.2 Sol, version details beyond the displayed model were not available) assisted during the November 23, 2026 Project 2 work with source collection and parsing, implementation, course verification, result presentation, and documentation. The student chose the final 60/40 research target, authored the pre-run changed-input prediction, and checked the original ALFRED release independently. The project keeps that check and the prediction separate from AI output. The student should approve the committee recommendation and present their reasoning in their own words.
