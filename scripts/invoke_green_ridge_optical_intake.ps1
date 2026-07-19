[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$GeneratedAtUtc,

    [Parameter(Mandatory = $true)]
    [string]$RunId,

    [string]$Quarantine,
    [string]$RawParent,
    [string]$StateFile,
    [string]$PythonExecutable
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$credentialRoot = Join-Path $env:LOCALAPPDATA 'BurnLens\credentials'

if (-not $Quarantine) {
    $Quarantine = Join-Path $repoRoot 'downloads\phase-two\quarantine\green-ridge-s2-optical-pair-v0.1.0'
}
if (-not $RawParent) {
    $RawParent = Join-Path $repoRoot 'downloads\phase-two\raw'
}
if (-not $StateFile) {
    $StateFile = Join-Path $repoRoot "downloads\phase-two\runs\$RunId.json"
}
if (-not $PythonExecutable) {
    $PythonExecutable = Join-Path $repoRoot '.venv\Scripts\python.exe'
}

$cdse = Import-Clixml -LiteralPath (Join-Path $credentialRoot 'cdse.credential.xml')
if ($cdse -isnot [System.Management.Automation.PSCredential]) {
    throw 'BurnLens CDSE credential file must contain a DPAPI-backed PSCredential object.'
}

$cdsePassword = $cdse.GetNetworkCredential().Password
try {
    $env:BURNLENS_CDSE_USERNAME = $cdse.UserName
    $env:BURNLENS_CDSE_PASSWORD = $cdsePassword

    & $PythonExecutable -m burnlens.acquire_green_ridge_optical `
        --quarantine $Quarantine `
        --raw-parent $RawParent `
        --state-file $StateFile `
        --generated-at-utc $GeneratedAtUtc `
        --run-id $RunId
    $exitCode = $LASTEXITCODE
}
finally {
    Remove-Item Env:BURNLENS_CDSE_USERNAME -ErrorAction SilentlyContinue
    Remove-Item Env:BURNLENS_CDSE_PASSWORD -ErrorAction SilentlyContinue
    $cdsePassword = $null
    $cdse = $null
}

exit $exitCode
