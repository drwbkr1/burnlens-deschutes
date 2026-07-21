[CmdletBinding()]
param(
    [ValidateSet('runtime', 'dev', 'geo-research')]
    [string]$Profile = 'dev'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$repoRoot = [System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$lockPath = Join-Path $repoRoot 'uv.lock'
$pythonPath = Join-Path $repoRoot '.venv\Scripts\python.exe'
$pythonPinPath = Join-Path $repoRoot '.python-version'
$verificationScript = Join-Path $repoRoot 'scripts\verify_environment.py'

if (-not (Test-Path -LiteralPath $lockPath -PathType Leaf)) {
    throw "Locked environment is missing: $lockPath"
}
if (-not (Test-Path -LiteralPath $pythonPinPath -PathType Leaf)) {
    throw "Python pin is missing: $pythonPinPath"
}
$expectedPython = (Get-Content -LiteralPath $pythonPinPath -Raw).Trim()

if (-not (Get-Command git -CommandType Application -ErrorAction SilentlyContinue)) {
    throw 'Git is required to verify the worktree root.'
}

$gitRoot = (& git -C $repoRoot rev-parse --show-toplevel 2>$null)
if ($LASTEXITCODE -ne 0 -or -not $gitRoot) {
    throw "The setup script must run from a BurnLens Git worktree: $repoRoot"
}
$gitRoot = [System.IO.Path]::GetFullPath($gitRoot.Trim())
if (-not $gitRoot.Equals($repoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Repository-root mismatch: script=$repoRoot git=$gitRoot"
}

$uvCommand = Get-Command uv -CommandType Application -ErrorAction SilentlyContinue
if (-not $uvCommand) {
    throw 'uv is required. Install uv, then rerun this script; the script never installs tools or copies credentials implicitly.'
}

$repoBytes = [System.Text.Encoding]::UTF8.GetBytes($repoRoot.ToLowerInvariant())
$hashAlgorithm = [System.Security.Cryptography.SHA256]::Create()
try {
    $repoDigest = [System.BitConverter]::ToString(
        $hashAlgorithm.ComputeHash($repoBytes)
    ).Replace('-', '').Substring(0, 24)
}
finally {
    $hashAlgorithm.Dispose()
}
$setupMutex = [System.Threading.Mutex]::new($false, "Local\BurnLensEnvironment-$repoDigest")
$mutexAcquired = $false
try {
    try {
        $mutexAcquired = $setupMutex.WaitOne(0)
    }
    catch [System.Threading.AbandonedMutexException] {
        $mutexAcquired = $true
    }
    if (-not $mutexAcquired) {
        throw "Another BurnLens environment setup is already running for this worktree: $repoRoot"
    }

    $venvRoot = Join-Path $repoRoot '.venv'
    if (Test-Path -LiteralPath $venvRoot) {
        if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
            throw "Existing .venv is incomplete. Move it aside explicitly before setup: $venvRoot"
        }
        $existingPython = (& $pythonPath -c 'import platform; print(platform.python_version())')
        if ($LASTEXITCODE -ne 0 -or -not $existingPython) {
            throw "Existing .venv Python could not be inspected: $pythonPath"
        }
        $existingPython = $existingPython.Trim()
        if ($existingPython -ne $expectedPython) {
            throw "Existing .venv uses Python $existingPython; expected $expectedPython. Move it aside explicitly before setup."
        }
    }

    $syncArguments = @('sync', '--locked')
    switch ($Profile) {
        'dev' {
            $syncArguments += @('--extra', 'dev')
        }
        'geo-research' {
            $syncArguments += @('--extra', 'dev', '--extra', 'geo-research')
        }
    }

    Push-Location $repoRoot
    try {
        & $uvCommand.Source @syncArguments
        if ($LASTEXITCODE -ne 0) {
            throw "uv sync failed for profile $Profile with exit code $LASTEXITCODE"
        }

        & $uvCommand.Source pip check --python $pythonPath
        if ($LASTEXITCODE -ne 0) {
            throw "Dependency integrity check failed for profile $Profile with exit code $LASTEXITCODE"
        }

        if (-not (Test-Path -LiteralPath $pythonPath -PathType Leaf)) {
            throw "Managed Python was not created: $pythonPath"
        }

        & $pythonPath $verificationScript --profile $Profile
        if ($LASTEXITCODE -ne 0) {
            throw "Environment verification failed for profile $Profile with exit code $LASTEXITCODE"
        }
    }
    finally {
        Pop-Location
    }

    Write-Output "BURNLENS_ENVIRONMENT_READY; profile=$Profile; python=.venv\Scripts\python.exe; lock=uv.lock"
}
finally {
    if ($mutexAcquired) {
        $setupMutex.ReleaseMutex()
    }
    $setupMutex.Dispose()
}
