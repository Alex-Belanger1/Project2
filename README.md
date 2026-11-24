# Project 2 — Investment Management Application

I used Codex to build and verify the implementation and prepare the exhibits. I chose the final tilt, wrote the changed-input prediction, and independently checked an ALFRED vintage.

This project is for education and does not provide investment advice.

The app screens allocations against the Meridian Foundation Reserve mandate and displays the separate tactical backtest. The recommendation is to **pilot the screening app for committee review and reject the tested FEDFUNDS tilt**. Read the [decision memo](docs/decision-memo.md), [allocation output](output/portfolio-screen.md), [holdout output](output/holdout.md), and [validation and AI use](docs/validation-and-ai-use.md).

From a checkout, with Python 3.10 or later, `python evaluate.py` reproduces the holdout report using the standard library and the committed data. It verifies the locked input hashes before processing. No API keys are needed.

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app opens on the verified bundled ETF data, with BIL and IEF selected as eligible under the Lab 15 assumptions. The sample contains 60 monthly returns ending September 2026. Use the sidebar to switch to the Meridian training fixture, change the return target or reserve minimum, or select the 36-month estimation window. Open **Baselines and mandate verdicts** to check each mix. For the demo, change the return target from 6.5% to 7.2%, show the defensive target's return verdict flip, then click **Reset to base** in the sidebar. The frozen holdout stays fixed. The development sensitivity controls adjust the signal cutoff and cost without rerunning the holdout.

Use `python evaluate.py --write` to regenerate the holdout Markdown and JSON. Run `python backtest.py` for the Lab 18 and 19 known answers, including the placebo and lag-zero leakage check. The [frozen rule](docs/frozen-rule.md), [data card](docs/data-provenance.md), and [submission manifest](docs/submission-manifest.md) are included.

The [course Project 2 requirements](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/projects/project-2-investment-management-application.md) govern the final submission.
