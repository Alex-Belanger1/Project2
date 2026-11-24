# Clean package check

On November 23, 2026, Codex verified a fresh copy of submission candidate `a47c44bf95b76f0dd5baff1d53c4996d760a3a69` under Windows with Python 3.10 and the pinned Streamlit dependency already installed. This is a repeatable portability check, separate from the student's independent source check.

| Check | Result |
| --- | --- |
| First failure | The sandbox blocked the Git-for-Windows subprocess during a local clone. No project code ran during that attempt. Exporting the committed tree with `git archive` and unpacking it into a fresh folder resolved the checkout issue. |
| Reproduce from the README | `python evaluate.py` verified the input hashes and matched the checked-in Markdown report. `python backtest.py` reproduced the training and leakage outputs. |
| Operate the interface | Streamlit AppTest launched the app from the fresh folder. It checked equal-weight and inverse-volatility numbers, the 7.2% control and verdict flip, and 7-day / 25 bp development controls. The holdout table remained unchanged. |
| Where the result appears | [Portfolio output](../output/portfolio-screen.md), [holdout output](../output/holdout.md), and the Frozen FEDFUNDS holdout panel of the app. |
| Time | 6.67 seconds for archive, extraction and automated checks on this machine, excluding dependency installation. |
