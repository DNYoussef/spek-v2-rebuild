# SPEK Platform v2 - Environment Validation Script
# Week 25 - Desktop Deployment
#
# This script validates that all required tools and configurations
# are present before starting the SPEK platform.

$ErrorActionPreference = "Continue"
$ValidationPassed = $true

# Colors
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "Cyan"

function Write-CheckResult {
    param(
        [bool]$Success,
        [string]$Message,
        [string]$Details = ""
    )

    if ($Success) {
        Write-Host "✓ $Message" -ForegroundColor $ColorSuccess
        if ($Details) {
            Write-Host "  $Details" -ForegroundColor DarkGray
        }
    } else {
        Write-Host "✗ $Message" -ForegroundColor $ColorError
        if ($Details) {
            Write-Host "  $Details" -ForegroundColor $ColorWarning
        }
        $script:ValidationPassed = $false
    }
}

Write-Host "`n========================================" -ForegroundColor $ColorInfo
Write-Host "SPEK Platform Environment Validation" -ForegroundColor $ColorInfo
Write-Host "========================================`n" -ForegroundColor $ColorInfo

# ============================================
# CHECK 1: Docker Tools
# ============================================
Write-Host "Checking Docker Tools..." -ForegroundColor $ColorInfo

$DockerInstalled = $null -ne (Get-Command "docker" -ErrorAction SilentlyContinue)
if ($DockerInstalled) {
    $DockerVersion = docker --version
    Write-CheckResult -Success $true -Message "Docker Tools installed" -Details $DockerVersion
} else {
    Write-CheckResult -Success $false -Message "Docker Tools not found" `
        -Details "Install from: https://docs.docker.com/engine/install/"
}

# Check Docker daemon
if ($DockerInstalled) {
    try {
        docker ps | Out-Null
        Write-CheckResult -Success $true -Message "Docker daemon is running"
    } catch {
        Write-CheckResult -Success $false -Message "Docker daemon is not running" `
            -Details "Start Docker Tools service"
    }
}

# ============================================
# CHECK 2: Docker Compose
# ============================================
Write-Host "`nChecking Docker Compose..." -ForegroundColor $ColorInfo

$ComposeInstalled = ($null -ne (Get-Command "docker-compose" -ErrorAction SilentlyContinue)) -or `
                    (docker compose version 2>&1 | Select-String "Docker Compose")

if ($ComposeInstalled) {
    try {
        $ComposeVersion = if (Get-Command "docker-compose" -ErrorAction SilentlyContinue) {
            docker-compose --version
        } else {
            docker compose version
        }
        Write-CheckResult -Success $true -Message "Docker Compose installed" -Details $ComposeVersion
    } catch {
        Write-CheckResult -Success $false -Message "Docker Compose not found" `
            -Details "Install Docker Compose plugin"
    }
} else {
    Write-CheckResult -Success $false -Message "Docker Compose not found" `
        -Details "Install Docker Compose plugin"
}

# ============================================
# CHECK 3: Node.js
# ============================================
Write-Host "`nChecking Node.js..." -ForegroundColor $ColorInfo

$NodeInstalled = $null -ne (Get-Command "node" -ErrorAction SilentlyContinue)
if ($NodeInstalled) {
    $NodeVersion = node --version
    $NodeVersionNumber = [version]($NodeVersion -replace 'v', '')

    if ($NodeVersionNumber.Major -ge 18) {
        Write-CheckResult -Success $true -Message "Node.js installed (v18+)" -Details $NodeVersion
    } else {
        Write-CheckResult -Success $false -Message "Node.js version too old (need v18+)" `
            -Details "Current: $NodeVersion, Required: v18+"
    }
} else {
    Write-CheckResult -Success $false -Message "Node.js not found" `
        -Details "Install from: https://nodejs.org/"
}

# ============================================
# CHECK 4: npm
# ============================================
Write-Host "`nChecking npm..." -ForegroundColor $ColorInfo

$NpmInstalled = $null -ne (Get-Command "npm" -ErrorAction SilentlyContinue)
if ($NpmInstalled) {
    $NpmVersion = npm --version
    Write-CheckResult -Success $true -Message "npm installed" -Details "v$NpmVersion"
} else {
    Write-CheckResult -Success $false -Message "npm not found" `
        -Details "npm should come with Node.js"
}

# ============================================
# CHECK 5: Network Ports
# ============================================
Write-Host "`nChecking network ports..." -ForegroundColor $ColorInfo

$RequiredPorts = @(3000, 5432, 6379)
foreach ($Port in $RequiredPorts) {
    $PortInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue

    if ($PortInUse) {
        Write-CheckResult -Success $false -Message "Port $Port is already in use" `
            -Details "Process: $($PortInUse.OwningProcess)"
    } else {
        Write-CheckResult -Success $true -Message "Port $Port is available"
    }
}

# ============================================
# CHECK 6: Environment File
# ============================================
Write-Host "`nChecking environment configuration..." -ForegroundColor $ColorInfo

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$EnvFile = Join-Path $ProjectRoot "atlantis-ui\.env"
$EnvExampleFile = Join-Path $ProjectRoot "atlantis-ui\.env.example"

if (Test-Path $EnvFile) {
    Write-CheckResult -Success $true -Message ".env file found" -Details $EnvFile

    # Check if .env has required variables
    $EnvContent = Get-Content $EnvFile -Raw
    $RequiredVars = @("DATABASE_URL", "REDIS_URL", "NODE_ENV")

    foreach ($Var in $RequiredVars) {
        if ($EnvContent -match "$Var\s*=\s*.+") {
            Write-CheckResult -Success $true -Message "$Var is configured"
        } else {
            Write-CheckResult -Success $false -Message "$Var is missing or empty" `
                -Details "Edit $EnvFile and set $Var"
        }
    }
} else {
    Write-CheckResult -Success $false -Message ".env file not found" `
        -Details "Copy $EnvExampleFile to $EnvFile and configure it"
}

# ============================================
# CHECK 7: AI CLI Tools (Optional)
# ============================================
Write-Host "`nChecking AI CLI tools (optional)..." -ForegroundColor $ColorInfo

# Gemini CLI
$GeminiInstalled = $null -ne (Get-Command "gemini" -ErrorAction SilentlyContinue)
if ($GeminiInstalled) {
    Write-CheckResult -Success $true -Message "Gemini CLI installed"
} else {
    Write-Host "  ℹ Gemini CLI not found (optional)" -ForegroundColor DarkGray
}

# Claude Code (via Cursor IDE)
$CursorInstalled = Test-Path "C:\Users\$env:USERNAME\AppData\Local\Programs\cursor"
if ($CursorInstalled) {
    Write-CheckResult -Success $true -Message "Cursor IDE installed (Claude Code)"
} else {
    Write-Host "  ℹ Cursor IDE not found (optional)" -ForegroundColor DarkGray
}

# ============================================
# CHECK 8: Disk Space
# ============================================
Write-Host "`nChecking disk space..." -ForegroundColor $ColorInfo

$Drive = (Get-Location).Drive.Name + ":"
$FreeSpace = (Get-PSDrive $Drive.TrimEnd(':')).Free / 1GB

if ($FreeSpace -gt 5) {
    Write-CheckResult -Success $true -Message "Sufficient disk space" `
        -Details "$([math]::Round($FreeSpace, 2)) GB available"
} else {
    Write-CheckResult -Success $false -Message "Low disk space" `
        -Details "Only $([math]::Round($FreeSpace, 2)) GB available (need 5+ GB)"
}

# ============================================
# CHECK 9: Memory
# ============================================
Write-Host "`nChecking available memory..." -ForegroundColor $ColorInfo

$TotalMemoryGB = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB
$FreeMemoryGB = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB / 1024

if ($TotalMemoryGB -ge 8) {
    Write-CheckResult -Success $true -Message "Sufficient memory" `
        -Details "$([math]::Round($TotalMemoryGB, 1)) GB total, $([math]::Round($FreeMemoryGB, 1)) GB free"
} else {
    Write-CheckResult -Success $false -Message "Low memory" `
        -Details "Only $([math]::Round($TotalMemoryGB, 1)) GB total (recommended: 8+ GB)"
}

# ============================================
# FINAL RESULT
# ============================================
Write-Host "`n========================================" -ForegroundColor $ColorInfo

if ($ValidationPassed) {
    Write-Host "✓ ALL CHECKS PASSED" -ForegroundColor $ColorSuccess
    Write-Host "`nYour system is ready to run SPEK Platform v2!" -ForegroundColor $ColorSuccess
    Write-Host "`nNext steps:" -ForegroundColor $ColorInfo
    Write-Host "1. Review and edit .env file if needed" -ForegroundColor Gray
    Write-Host "2. Run: .\start-spek.ps1" -ForegroundColor Gray
    exit 0
} else {
    Write-Host "✗ VALIDATION FAILED" -ForegroundColor $ColorError
    Write-Host "`nPlease fix the issues above before continuing." -ForegroundColor $ColorWarning
    Write-Host "`nFor help, see: docs/DESKTOP-DEPLOYMENT.md" -ForegroundColor $ColorInfo
    exit 1
}
