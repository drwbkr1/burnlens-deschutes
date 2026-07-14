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
    $Quarantine = Join-Path $repoRoot 'downloads\phase-two\quarantine\darlene3-s2-viirs-pair-v0.1.0'
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
$earthdata = Import-Clixml -LiteralPath (Join-Path $credentialRoot 'earthdata.credential.xml')
if ($cdse -isnot [System.Management.Automation.PSCredential] -or
    $earthdata -isnot [System.Management.Automation.PSCredential]) {
    throw 'BurnLens credential files must contain DPAPI-backed PSCredential objects.'
}

$cdsePassword = $cdse.GetNetworkCredential().Password
$earthdataPassword = $earthdata.GetNetworkCredential().Password

try {
    $env:BURNLENS_CDSE_USERNAME = $cdse.UserName
    $env:BURNLENS_CDSE_PASSWORD = $cdsePassword
    $env:BURNLENS_EARTHDATA_USERNAME = $earthdata.UserName
    $env:BURNLENS_EARTHDATA_PASSWORD = $earthdataPassword

    & $PythonExecutable -m burnlens.acquire_provider_package `
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
    Remove-Item Env:BURNLENS_EARTHDATA_USERNAME -ErrorAction SilentlyContinue
    Remove-Item Env:BURNLENS_EARTHDATA_PASSWORD -ErrorAction SilentlyContinue
    $cdsePassword = $null
    $earthdataPassword = $null
    $cdse = $null
    $earthdata = $null
}

exit $exitCode
