# Rubric

Applied by a reviewer reading your diff against `baseline`. The grader scores what
tests can see; this covers what they cannot. Five items, equal weight.

- **R1 — Transform logic lives in the transforms.** New logic belongs in
  `src/retail_pipeline/` functions, not inlined into the runner or the tests.
- **R2 — Schema contracts respected.** Explicit types throughout; no `inferSchema`;
  money stays decimal; output columns exactly as specified.
- **R3 — Malformed input is handled at the edge.** Cleaning concerns stay in the
  cleaning stage; downstream transforms assume clean input rather than re-guarding
  every column.
- **R4 — You added tests of your own.** At least one meaningful case the shipped
  suite does not cover (for example: a resend arriving twice, or a store-day with no
  sales).
- **R5 — The diff reads like the codebase.** Small focused functions, the existing
  style, no wholesale reformatting, no dead code, no leftover debug output.
