# Bug reports

Bug tests are already written and failing (`tests/`). A bug earns its points when its
category passes. The report describes what users see — finding the cause is part of
the work.

## B1 — Doubled revenue after a feed resend (20 points)

Filed by: finance ops

On 2026-03-15 the overnight totals for business date 2026-03-14 came in almost
exactly double what the stores reported. The 2026-03-14 feed had been re-sent that
morning after an upstream correction, and everyone expected the resend to *replace*
the original rows — the pipeline has a de-duplication step for exactly this case.

There is a second symptom: the upstream correction changed the quantity on
transaction `T-1006`, but our numbers still show the old value wherever that
transaction appears.

**Expected**

- A transaction delivered more than once counts once.
- When deliveries disagree, the most recently ingested version is the one that
  counts.
