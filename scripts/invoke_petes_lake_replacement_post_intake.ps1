[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$GeneratedAtUtc,

    [string]$PythonExecutable
)

$ErrorActionPreference = 'Stop'
$repoRoot = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$credentialRoot = Join-Path $env:LOCALAPPDATA 'BurnLens\credentials'
$wrapperExitCode = 3
$transactionExitCode = 3
$cdse = $null
$cdsePassword = $null

if (-not $PythonExecutable) {
    $PythonExecutable = Join-Path $repoRoot '.venv\Scripts\python.exe'
}
$PythonExecutable = [System.IO.Path]::GetFullPath($PythonExecutable)
$repoPrefix = $repoRoot.TrimEnd('\') + '\'
if (-not $PythonExecutable.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    [Console]::Error.WriteLine('PETES_LAKE_REPLACEMENT_WRAPPER_FAILURE; reason=PYTHON_OUTSIDE_REPOSITORY')
    exit 3
}
if (-not (Test-Path -LiteralPath $PythonExecutable -PathType Leaf)) {
    [Console]::Error.WriteLine('PETES_LAKE_REPLACEMENT_WRAPPER_FAILURE; reason=PYTHON_NOT_FOUND')
    exit 3
}

try {
    # Run every repository, remote, source, terms, metadata, path, and original-
    # pre custody gate before DPAPI material is imported.
    & $PythonExecutable -m burnlens.acquire_petes_lake_replacement_post `
        --repository-root $repoRoot `
        --generated-at-utc $GeneratedAtUtc `
        --revision r001 `
        --mode acquire `
        --preflight-only
    if ($LASTEXITCODE -ne 0) {
        throw [System.InvalidOperationException]::new('PETES_LAKE_REPLACEMENT_PREFLIGHT_FAILED')
    }

    $cdse = Import-Clixml -LiteralPath (Join-Path $credentialRoot 'cdse.credential.xml')
    if ($cdse -isnot [System.Management.Automation.PSCredential]) {
        throw [System.InvalidOperationException]::new('PETES_LAKE_REPLACEMENT_CDSE_CREDENTIAL_INVALID')
    }

    $cdsePassword = $cdse.GetNetworkCredential().Password
    try {
        $env:BURNLENS_CDSE_USERNAME = $cdse.UserName
        $env:BURNLENS_CDSE_PASSWORD = $cdsePassword

        & $PythonExecutable -m burnlens.acquire_petes_lake_replacement_post `
            --repository-root $repoRoot `
            --generated-at-utc $GeneratedAtUtc `
            --revision r001 `
            --mode acquire
        $transactionExitCode = $LASTEXITCODE
    }
    finally {
        Remove-Item Env:BURNLENS_CDSE_USERNAME -ErrorAction SilentlyContinue
        Remove-Item Env:BURNLENS_CDSE_PASSWORD -ErrorAction SilentlyContinue
        $cdsePassword = $null
        $cdse = $null
    }

    if ($transactionExitCode -ne 0) {
        $wrapperExitCode = $transactionExitCode
    }
    else {
        # Reopen both archives and recompute private/public binding without a credential.
        & $PythonExecutable -m burnlens.acquire_petes_lake_replacement_post `
            --repository-root $repoRoot `
            --generated-at-utc $GeneratedAtUtc `
            --revision r001 `
            --mode acquire `
            --verify-only
        if ($LASTEXITCODE -ne 0) {
            throw [System.InvalidOperationException]::new('PETES_LAKE_REPLACEMENT_FINAL_VERIFY_FAILED')
        }
        $wrapperExitCode = 0
    }
}
catch {
    [Console]::Error.WriteLine("PETES_LAKE_REPLACEMENT_WRAPPER_FAILURE; type=$($_.Exception.GetType().Name)")
    $wrapperExitCode = 3
}
finally {
    Remove-Item Env:BURNLENS_CDSE_USERNAME -ErrorAction SilentlyContinue
    Remove-Item Env:BURNLENS_CDSE_PASSWORD -ErrorAction SilentlyContinue
    $cdsePassword = $null
    $cdse = $null
}

exit $wrapperExitCode
