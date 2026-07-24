[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RequestedAtUtc,

    [Parameter(Mandatory = $true)]
    [string]$GitSourceCommit,

    [string]$PythonExecutable
)

$ErrorActionPreference = 'Stop'
$repoRoot = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$recipient = $null

if (-not $PythonExecutable) {
    $PythonExecutable = Join-Path $repoRoot '.venv\Scripts\python.exe'
}
$PythonExecutable = [System.IO.Path]::GetFullPath($PythonExecutable)
$repoPrefix = $repoRoot.TrimEnd('\') + '\'
if (-not $PythonExecutable.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    [Console]::Error.WriteLine('WARD_CREEK_U03_REQUEST_FAILURE; reason=PYTHON_OUTSIDE_REPOSITORY')
    exit 3
}

try {
    $recipient = git -C $repoRoot config user.email
    if (-not $recipient) {
        throw [System.InvalidOperationException]::new('WARD_CREEK_U03_RECIPIENT_MISSING')
    }
    $env:BURNLENS_REFERENCE_REQUEST_EMAIL = $recipient
    & $PythonExecutable -m burnlens.request_replacement_event_reference `
        --repository-root $repoRoot `
        --requested-at-utc $RequestedAtUtc `
        --run-id 'BL-2026-07-24-ward-creek-reference-request-r001' `
        --git-source-commit $GitSourceCommit
    exit $LASTEXITCODE
}
catch {
    [Console]::Error.WriteLine("WARD_CREEK_U03_REQUEST_FAILURE; type=$($_.Exception.GetType().Name)")
    exit 3
}
finally {
    Remove-Item Env:BURNLENS_REFERENCE_REQUEST_EMAIL -ErrorAction SilentlyContinue
    $recipient = $null
}
