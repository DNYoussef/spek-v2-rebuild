# ============================================================================
# SPEK Platform Desktop Shortcut Creator
# Version: 1.0.0
# Description: Creates a desktop shortcut for one-click SPEK Platform launch
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "🔗 Creating SPEK Platform Desktop Shortcut" -ForegroundColor Cyan
Write-Host ""

# Get the current directory (project root)
$projectRoot = $PSScriptRoot
$launcherPath = Join-Path $projectRoot "spek-launcher.ps1"

# Check if launcher exists
if (-not (Test-Path $launcherPath)) {
    Write-Host "✗ Error: spek-launcher.ps1 not found in $projectRoot" -ForegroundColor Red
    Write-Host "  Please ensure you're running this script from the project root directory." -ForegroundColor Yellow
    exit 1
}

# Get desktop path
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "SPEK Platform.lnk"

# Create shortcut
Write-Host "→ Creating shortcut at: $shortcutPath" -ForegroundColor Yellow

$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut($shortcutPath)

# PowerShell execution command
$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-ExecutionPolicy Bypass -NoProfile -File `"$launcherPath`""
$shortcut.WorkingDirectory = $projectRoot
$shortcut.Description = "Launch SPEK Platform v2 + Atlantis UI"
$shortcut.IconLocation = "powershell.exe,0"

# Save shortcut
$shortcut.Save()

Write-Host ""
Write-Host "✓ Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Shortcut Location: $shortcutPath" -ForegroundColor Cyan
Write-Host "🎯 Target Script: $launcherPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now double-click 'SPEK Platform' on your desktop to start the platform!" -ForegroundColor Yellow
Write-Host ""
