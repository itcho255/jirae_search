# PowerShell script: Create a Startup shortcut to run the clock on login
# Usage: Run this script in PowerShell (may require ExecutionPolicy). It will
# attempt to locate `pythonw` (no console window) or `python` in PATH.
# If neither is in PATH, set $pythonPath.

$scriptPath = Join-Path $PSScriptRoot 'clock.py'

# Prefer pythonw.exe so no console window flashes on login
$pythonCmd = (Get-Command pythonw -ErrorAction SilentlyContinue).Source
if (-not $pythonCmd) {
    $pythonCmd = (Get-Command python -ErrorAction SilentlyContinue).Source
}
if (-not $pythonCmd) {
    Write-Host "python/pythonw not found in PATH. Please edit this script and set `$pythonPath` to your python.exe path." -ForegroundColor Yellow
    $pythonPath = ''
} else {
    $pythonPath = $pythonCmd
}

if (-not (Test-Path $scriptPath)) {
    Write-Host "clock.py not found in script folder: $scriptPath" -ForegroundColor Red
    exit 1
}

$startup = [Environment]::GetFolderPath('Startup')
$lnkPath = Join-Path $startup 'DesktopClock.lnk'

$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($lnkPath)
$shortcut.TargetPath = $pythonPath
$shortcut.Arguments = "`"$scriptPath`""
$shortcut.WorkingDirectory = $PSScriptRoot
$shortcut.IconLocation = "$env:SystemRoot\system32\shell32.dll, 1"
$shortcut.Save()

Write-Host "Shortcut created:" $lnkPath -ForegroundColor Green
