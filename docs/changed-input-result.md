# Changed-input result — annual return target

The [student's verbatim prediction](changed-input-prediction.md) was saved in local commit `b8736fd36489a1d330d46a7ad0f84939d2019a70` on November 23, 2026 at 19:39:24 Eastern, before running the changed case. The student expected a feasible allocation of 80% equity / 20% bonds, higher return and risk, and a recommendation to increase equity exposure.

In the Streamlit app, change only **Annual return objective (%)** from **6.5% to 7.2%**. Keep the verified full monthly sample, 3% reserve floor, BIL and IEF reserve eligibility, and the 5-point search grid. The UI results were checked against the common engine. [Machine-readable record](../output/changed-input.json).

| Case | BIL | IEF | LQD | VT | Estimated annual return | Estimated annual volatility | Eligible reserve |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 6.5% target | 60% | 0% | 0% | 40% | 6.91% | 6.04% | 60% |
| 7.2% target | 55% | 0% | 0% | 45% | 7.33% | 6.78% | 55% |

Feasibility and the directions of the estimated return, estimated volatility, and equity-weight changes matched the prediction. The actual move was **5 points into equity**, versus the predicted 40-point increase from the baseline. The 7.2% target is high enough to rule out the old 60/40 candidate. The optimizer found a lower-risk way to meet the new target with 45% equity. The actual result retains Treasury-bill exposure via BIL and holds neither IEF nor LQD. Estimated return rose about 0.42 percentage points and estimated volatility about 0.74 points. This static calculation does not establish a change in realized drawdown.

**Decision effect.** If the committee adopts a 7.2% screening target, put 55% BIL / 45% VT forward as the minimum-volatility candidate on these estimates, subject to the unresolved policy checks. The change does not support an 80% equity allocation on this screen. The frozen historical result still supports rejecting the FEDFUNDS overlay.

**Independent arithmetic explanation of the miss.** The frozen sample estimates BIL at about 3.5943% and VT at 11.8952%. Within the BIL/VT pair, the estimated return reaches 7.2% at about 43.44% VT, so 45% is the first qualifying equity weight on the 5-point grid. This calculation explains the result after the run. It is separate from the student's pre-run prediction.
