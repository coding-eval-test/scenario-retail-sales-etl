# Retail Sales ETL — scenario

You've joined a data engineering team that owns a nightly retail sales pipeline. The
extract and cleaning stages work and are tested. Your job: build the summary tables the
business is waiting on, and fix a de-duplication defect that doubled a day's revenue.

Read these, in order:

1. `docs/domain.md` — the pipeline, the feeds, the ground rules
2. `docs/user-stories.md` — S1, S2
3. `docs/bug-reports.md` — B1
4. `docs/rubric.md` — what a reviewer looks for beyond the tests

## Stack

Python 3.11 · PySpark 3.5 · pytest. The devcontainer (or a Codespace) has everything
preinstalled — this is the supported path. Working locally instead: install a JDK 17
and Python 3.11, then `pip install -r requirements.txt`. The pipeline and its tests
never write files through Spark, so no Hadoop/winutils setup is needed on Windows.

## Getting started

```bash
pip install -r requirements.txt        # already done for you in the devcontainer
python -m retail_pipeline.run_pipeline # run the pipeline over data/raw and print results
python -m pytest                       # run everything (ships partly red — that's the work)
./scripts/check.sh                     # per-work-item summary (scripts\check.ps1 on Windows)
```

## Your work

Everything you need to change lives in `src/retail_pipeline/`. The tests in `tests/`
define the output contracts exactly — column names, types, values. How you build the
DataFrames is your call: the DataFrame API and `spark.sql` over temp views are both
fine. Run one work item at a time with `python -m pytest -m S1` (likewise `S2`, `B1`,
`Regression`).

## Grading

Every push runs the `Grade` workflow and writes a scorecard to the run summary. A work
item earns its points only when its whole category passes. Skipping tests doesn't help:
any skipped test zeroes its category.

<!-- grading-table:start -->
| Work item | Points |
| --- | --- |
| S1 — Daily store sales summary | 25 |
| S2 — Product enrichment | 25 |
| B1 — Doubled revenue after a feed resend | 20 |
| Regression — existing pipeline behavior | 30 |
<!-- grading-table:end -->

Breaking the extract or cleaning stages costs you the 30 Regression points — extending
without breaking is the job.
