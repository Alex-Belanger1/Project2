# Project 2 — Investment Management Application

Codex helped assemble the starter tool and draft the evaluation design. This is a course project and a learning demonstration for education, not investment advice.

This workspace starts from the verified Lab 15 portfolio engine. [Draft project design](docs/project-design.md) describes the mandate, FEDFUNDS hypothesis, backtest, and acceptance criteria before any strategy run. The app shows allocation estimates, baseline comparisons, and rule-by-rule mandate verdicts.

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app opens on the bundled ETF data, with BIL and IEF selected as eligible under the Lab 15 assumptions. The sample contains 60 monthly returns ending September 2026. Use the sidebar to switch to the Meridian training inputs or upload another CSV. Run `python backtest.py` for the Lab 18 and 19 known answers, including the placebo and lag-zero leakage check. The [course Project 2 requirements](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/projects/project-2-investment-management-application.md) govern the final submission.
