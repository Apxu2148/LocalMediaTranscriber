[CmdletBinding()]
param(
    [switch]$StopOnly
)

$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$ProjectRoot = $ProjectRoot.TrimEnd([char[]]@("\", "/"))
$ProjectRootLower = $ProjectRoot.ToLowerInvariant()
$ProjectRootForwardLower = $ProjectRoot.Replace("\", "/").ToLowerInvariant()
$ProcessSnapshotReadFailed = $false

function Test-CommandLineReferencesProject {
    param(
        [AllowNull()]
        [string]$CommandLine
    )

    if ([string]::IsNullOrWhiteSpace($CommandLine)) {
        return $false
    }

    $lower = $CommandLine.ToLowerInvariant()
    return $lower.Contains($script:ProjectRootLower) -or $lower.Contains($script:ProjectRootForwardLower)
}

function Test-IsUnderProjectRoot {
    param(
        [string]$Path
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path).TrimEnd([char[]]@("\", "/"))
    $rootWithBackslash = "$script:ProjectRoot\"
    $rootWithSlash = "$($script:ProjectRoot.Replace("\", "/"))/"
    $fullPathForward = $fullPath.Replace("\", "/")

    return $fullPath.Equals($script:ProjectRoot, [System.StringComparison]::OrdinalIgnoreCase) `
        -or $fullPath.StartsWith($rootWithBackslash, [System.StringComparison]::OrdinalIgnoreCase) `
        -or $fullPathForward.StartsWith($rootWithSlash, [System.StringComparison]::OrdinalIgnoreCase)
}

function Get-ProcessSnapshot {
    try {
        $script:ProcessSnapshotReadFailed = $false
        return @(Get-CimInstance Win32_Process -ErrorAction Stop)
    } catch {
        $script:ProcessSnapshotReadFailed = $true
        Write-Warning "Could not read process command lines: $($_.Exception.Message)"
        return @()
    }
}

function Get-ProjectServerProcesses {
    $serverNames = @("python.exe", "pythonw.exe", "uvicorn.exe", "uvicorn")

    Get-ProcessSnapshot | Where-Object {
        $name = [string]$_.Name
        $commandLine = [string]$_.CommandLine
        (Test-CommandLineReferencesProject $commandLine) -and (
            $serverNames -contains $name.ToLowerInvariant() -or $commandLine -match "(?i)\buvicorn\b"
        )
    }
}

function Stop-ProjectServerProcesses {
    Write-Host "Stopping Local Media Transcriber processes..."
    $targets = @(Get-ProjectServerProcesses | Sort-Object ProcessId -Unique)

    if ($targets.Count -eq 0) {
        if ($script:ProcessSnapshotReadFailed) {
            Write-Warning "No processes were stopped because process command lines could not be read safely."
        }
        Write-Host "No Local Media Transcriber processes found."
        return
    }

    foreach ($process in $targets) {
        Write-Host ("Found process: {0} {1} {2}" -f $process.ProcessId, $process.Name, $process.CommandLine)
        try {
            Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop
            Write-Host "Stopped."
        } catch {
            Write-Warning ("Could not stop PID {0}: {1}" -f $process.ProcessId, $_.Exception.Message)
        }
    }

    Write-Host "Done."
}

function Remove-ProjectPycacheDirectories {
    Write-Host "Removing project __pycache__ directories..."
    $cacheRoots = @("app", "tests", "scripts") |
        ForEach-Object { Join-Path $ProjectRoot $_ } |
        Where-Object { Test-Path -LiteralPath $_ }
    $cacheDirs = @(
        foreach ($cacheRoot in $cacheRoots) {
            Get-ChildItem -LiteralPath $cacheRoot -Directory -Filter "__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
        }
    )

    if ($cacheDirs.Count -eq 0) {
        Write-Host "No __pycache__ directories found."
        return
    }

    foreach ($directory in $cacheDirs) {
        $resolved = (Resolve-Path -LiteralPath $directory.FullName).Path
        if (-not (Test-IsUnderProjectRoot $resolved)) {
            Write-Warning "Skipped path outside project root: $resolved"
            continue
        }

        try {
            Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction Stop
            Write-Host "Removed: $resolved"
        } catch {
            Write-Warning "Could not remove ${resolved}: $($_.Exception.Message)"
        }
    }
}

function Remove-PytestCache {
    $pytestCache = Join-Path $ProjectRoot ".pytest_cache"
    if (-not (Test-Path -LiteralPath $pytestCache)) {
        Write-Host "No .pytest_cache directory found."
        return
    }

    $resolved = (Resolve-Path -LiteralPath $pytestCache).Path
    if (-not (Test-IsUnderProjectRoot $resolved)) {
        Write-Warning "Skipped .pytest_cache outside project root: $resolved"
        return
    }

    try {
        Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction Stop
        Write-Host "Removed: $resolved"
    } catch {
        Write-Warning "Could not remove ${resolved}: $($_.Exception.Message)"
    }
}

function Get-RelatedGitLockProcesses {
    $lockProcessNames = @("git.exe", "ssh.exe", "gpg.exe", "codex.exe")

    Get-ProcessSnapshot | Where-Object {
        $name = ([string]$_.Name).ToLowerInvariant()
        ($lockProcessNames -contains $name) -and (Test-CommandLineReferencesProject ([string]$_.CommandLine))
    }
}

function Remove-GitIndexLockIfSafe {
    $lockPath = Join-Path $ProjectRoot ".git\index.lock"
    if (-not (Test-Path -LiteralPath $lockPath)) {
        Write-Host "No .git/index.lock found."
        return
    }

    $script:ProcessSnapshotReadFailed = $false
    $relatedProcesses = @(Get-RelatedGitLockProcesses | Sort-Object ProcessId -Unique)
    if ($script:ProcessSnapshotReadFailed) {
        Write-Warning "Not removing .git/index.lock because process command lines could not be read safely."
        return
    }
    if ($relatedProcesses.Count -gt 0) {
        Write-Warning "Not removing .git/index.lock because related git/ssh/gpg/codex processes are active."
        foreach ($process in $relatedProcesses) {
            Write-Warning ("Active process: {0} {1} {2}" -f $process.ProcessId, $process.Name, $process.CommandLine)
        }
        return
    }

    $resolvedLock = (Resolve-Path -LiteralPath $lockPath).Path
    if (-not (Test-IsUnderProjectRoot $resolvedLock)) {
        Write-Warning "Skipped Git lock outside project root: $resolvedLock"
        return
    }

    try {
        Remove-Item -LiteralPath $resolvedLock -Force -ErrorAction Stop
        Write-Host "Removed stale Git lock: $resolvedLock"
    } catch {
        Write-Warning "Could not remove Git lock ${resolvedLock}: $($_.Exception.Message)"
    }
}

function Show-GitStatus {
    Write-Host "git status --short:"
    try {
        & git -C $ProjectRoot status --short
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "git status exited with code $LASTEXITCODE."
        }
    } catch {
        Write-Warning "Could not run git status: $($_.Exception.Message)"
    }
}

Stop-ProjectServerProcesses

if (-not $StopOnly) {
    Remove-ProjectPycacheDirectories
    Remove-PytestCache
    Remove-GitIndexLockIfSafe
    Show-GitStatus
}
