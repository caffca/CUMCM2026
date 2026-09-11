$ErrorActionPreference = 'Stop'

Write-Output 'Checking formal Q1-Q3 validation snapshots...'
$checks = @(
    @{ Path = 'outputs/q1/validation.json'; Expected = 'PASS' },
    @{ Path = 'outputs/q2/validation.json'; Expected = 'PASS' },
    @{ Path = 'outputs/q3/validation.json'; Expected = 'PASS' }
)
foreach ($item in $checks) {
    if (-not (Test-Path -LiteralPath $item.Path)) { throw "Missing $($item.Path)" }
    $text = Get-Content -Raw -LiteralPath $item.Path
    $match = [regex]::Match($text, '"status"\s*:\s*"([^"]+)"')
    if (-not $match.Success -or $match.Groups[1].Value -ne $item.Expected) { throw "$($item.Path): status is not $($item.Expected)" }
    Write-Output "$($item.Path): $($match.Groups[1].Value)"
}
$q1Text = Get-Content -Raw outputs/q1/results.json
$q2Text = Get-Content -Raw outputs/q2/results.json
$q3Text = Get-Content -Raw outputs/q3/validation.json
$q1Count = [regex]::Match($q1Text, '"conflict_pair_count"\s*:\s*(\d+)').Groups[1].Value
$q2Count = [regex]::Match($q2Text, '"revocations"\s*:\s*(\d+)').Groups[1].Value
$q3Count = [regex]::Match($q3Text, '"new_plan_count"\s*:\s*(\d+)').Groups[1].Value
Write-Output ("Q1 conflict pairs: {0}" -f $q1Count)
Write-Output ("Q2 revocations: {0}" -f $q2Count)
Write-Output ("Q3 additions: {0}" -f $q3Count)
Write-Output 'Package check completed.'
