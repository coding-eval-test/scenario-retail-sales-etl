# Runs the same per-category checks the grader runs.
$ErrorActionPreference = 'Continue'

$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
# Timestamps collect via the process-local timezone; pin it so results match CI.
$env:TZ = 'UTC'
$manifest = Join-Path $root 'scenario.json'

if (-not (Test-Path $manifest)) {
    Write-Host "scenario.json not found at $manifest - cannot tell which work items to check."
    exit 1
}

# scenario.json is the same file the grader reads.
$categories = (Get-Content $manifest -Raw | ConvertFrom-Json).categories.category

if (-not $categories) {
    Write-Host "No work items found in $manifest. Expected 'category' entries - is the file valid JSON?"
    exit 1
}

Write-Host 'Building...'
python -m compileall -q src tests
if ($LASTEXITCODE -ne 0) {
    Write-Host 'BUILD FAILED - fix the syntax errors before running the checks.'
    Write-Host '(If imports are missing, run: pip install -r requirements.txt)'
    exit 1
}

$results = [ordered]@{}
$overall = 0

foreach ($category in $categories) {
    Write-Host ''
    Write-Host "=== $category ==="
    if (Test-Path (Join-Path $root 'reports')) {
        Remove-Item -Recurse -Force (Join-Path $root 'reports')
    }
    python -m pytest -m $category --junitxml="reports/$category.xml"
    $suitePassed = ($LASTEXITCODE -eq 0)

    # An unmatched marker exits 5 (not a failure), so the exit code alone cannot
    # be trusted in either direction. executed = tests - skipped from the report
    # is what tells "all passed" from "none ran" from "some dodged": any skipped
    # test zeroes the category, same as the grader.
    $report = Join-Path $root "reports/$category.xml"
    $tests = 0
    $skipped = 0
    if (Test-Path $report) {
        $suite = ([xml](Get-Content $report -Raw)).SelectSingleNode('//testsuite')
        if ($suite) {
            $tests = [int]$suite.tests
            $skipped = [int]$suite.skipped
        }
    }
    $executed = $tests - $skipped

    if ($executed -le 0) {
        $results[$category] = 'NO TESTS'
        $overall = 1
    }
    elseif ($skipped -gt 0) {
        $results[$category] = 'SKIPPED'
        $overall = 1
    }
    elseif ($suitePassed) {
        $results[$category] = 'PASS'
    }
    else {
        $results[$category] = 'FAIL'
        $overall = 1
    }
}

Write-Host ''
Write-Host '================ SUMMARY ================'
foreach ($category in $categories) {
    '{0,-12} {1}' -f $category, $results[$category] | Write-Host
}
Write-Host '========================================'

exit $overall
}
finally {
    Pop-Location
}
