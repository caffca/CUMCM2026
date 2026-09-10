[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$MilestoneSha
)

$ErrorActionPreference = 'Stop'

$BuilderRepo = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$ReviewWorktree = Join-Path (Split-Path $BuilderRepo -Parent) ((Split-Path $BuilderRepo -Leaf) + '-review')

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string[]]$Arguments
    )

    $result = & git -C $BuilderRepo @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git failed: git -C `"$BuilderRepo`" $($Arguments -join ' ')`n$result"
    }
    return @($result)
}

if (-not (Test-Path -LiteralPath (Join-Path $BuilderRepo '.git'))) {
    throw "Builder repository is not a Git repository: $BuilderRepo"
}

$resolved = & git -C $BuilderRepo rev-parse --verify --quiet "$MilestoneSha^{commit}" 2>$null
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($resolved -join ''))) {
    throw "Milestone SHA does not resolve to a commit in the Builder repository: $MilestoneSha"
}
$ResolvedSha = ($resolved | Select-Object -First 1).Trim()

$reviewExists = Test-Path -LiteralPath $ReviewWorktree
if (-not $reviewExists) {
    Invoke-Git @('worktree', 'add', '--detach', $ReviewWorktree, $ResolvedSha) | Out-Host
}
else {
    $reviewPath = [System.IO.Path]::GetFullPath($ReviewWorktree).TrimEnd('\')
    $records = Invoke-Git @('worktree', 'list', '--porcelain')
    $registered = $false
    foreach ($line in $records) {
        if ($line -like 'worktree *') {
            $candidate = $line.Substring(9).Trim()
            try { $candidate = [System.IO.Path]::GetFullPath($candidate).TrimEnd('\') } catch { }
            if ($candidate -ieq $reviewPath) { $registered = $true; break }
        }
    }
    if (-not $registered) {
        throw "Review path exists but is not the registered worktree for this repository; refusing to overwrite: $ReviewWorktree"
    }

    $dirty = & git -C $ReviewWorktree status --porcelain 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Cannot inspect Reviewer worktree; refusing to switch: $ReviewWorktree`n$dirty"
    }
    if (-not [string]::IsNullOrWhiteSpace(($dirty -join ''))) {
        throw "Reviewer worktree is dirty; refusing to switch: $ReviewWorktree"
    }

    $reviewRepo = & git -C $ReviewWorktree rev-parse --show-toplevel 2>&1
    if ($LASTEXITCODE -ne 0 -or ([System.IO.Path]::GetFullPath(($reviewRepo | Select-Object -First 1).Trim()).TrimEnd('\') -ine $reviewPath)) {
        throw "Reviewer path is not a valid worktree checkout: $ReviewWorktree"
    }
    & git -C $ReviewWorktree switch --detach $ResolvedSha 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Could not switch clean Reviewer worktree to $ResolvedSha"
    }
}

$finalSha = & git -C $ReviewWorktree rev-parse HEAD 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "Could not read final frozen SHA from Reviewer worktree: $ReviewWorktree"
}

Write-Output "Review worktree: $ReviewWorktree"
Write-Output "Frozen SHA: $($finalSha | Select-Object -First 1)"
