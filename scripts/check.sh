#!/usr/bin/env bash
# Runs the same per-category checks the grader runs.
set -uo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root" || exit 1
# Timestamps collect via the process-local timezone; pin it so results match CI.
export TZ=UTC
manifest="$root/scenario.json"

if [ ! -f "$manifest" ]; then
  echo "scenario.json not found at ${manifest} — cannot tell which work items to check."
  exit 1
fi

# scenario.json is the same file the grader reads. Parsed with sed rather than jq
# because jq is not installed everywhere this runs; CI keeps the file in the
# one-key-per-line shape this depends on.
categories=$(sed -n 's/.*"category"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$manifest")

if [ -z "$categories" ]; then
  echo "No work items found in ${manifest}. Expected \"category\" entries — is the file valid JSON?"
  exit 1
fi

declare -A results
overall=0

echo "Building..."
if ! python -m compileall -q src tests; then
  echo "BUILD FAILED — fix the syntax errors before running the checks."
  echo "(If imports are missing, run: pip install -r requirements.txt)"
  exit 1
fi

for category in $categories; do
  echo ""
  echo "=== ${category} ==="
  rm -rf reports
  if python -m pytest -m "${category}" --junitxml="reports/${category}.xml" < /dev/null; then
    suite_passed=1
  else
    suite_passed=0
  fi

  # An unmatched marker exits 5 (not a failure), so the exit code alone cannot be
  # trusted in either direction. executed = tests - skipped from the report is
  # what tells "all passed" from "none ran" from "some dodged": any skipped test
  # zeroes the category, same as the grader.
  report="reports/${category}.xml"
  tests=""
  skipped=""
  if [ -e "$report" ]; then
    tests=$(sed -n 's/.*<testsuite [^>]*tests="\([0-9]*\)".*/\1/p' "$report" | head -1)
    skipped=$(sed -n 's/.*<testsuite [^>]*skipped="\([0-9]*\)".*/\1/p' "$report" | head -1)
  fi
  executed=$(( ${tests:-0} - ${skipped:-0} ))

  if [ "$executed" -le 0 ]; then
    results[$category]="NO TESTS"
    overall=1
  elif [ "${skipped:-0}" -gt 0 ]; then
    results[$category]="SKIPPED"
    overall=1
  elif [ "$suite_passed" -eq 1 ]; then
    results[$category]="PASS"
  else
    results[$category]="FAIL"
    overall=1
  fi
done

echo ""
echo "================ SUMMARY ================"
for category in $categories; do
  printf '%-12s %s\n' "$category" "${results[$category]}"
done
echo "========================================"

exit $overall
