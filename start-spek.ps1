# SPEK Platform v2 + Atlantis UI - Desktop Launcher
# Week 25 - Desktop Deployment
#
# This script starts the SPEK platform in desktop mode using:
# - Docker Tools (NOT Docker Desktop)
# - Local PostgreSQL + Redis containers
# - AI CLI integration (Claude Code, Gemini CLI, Codex CLI)

param(
    [switch]$SkipDocker,
    [switch]$SkipBrowser,
    [switch]$Verbose
)

# ============================================
# CONFIGURATION
# ============================================

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$AtlantisUIPath = Join-Path $ProjectRoot "atlantis-ui"
$EnvFile = Join-Path $AtlantisUIPath ".env"
$EnvExampleFile = Join-Path $AtlantisUIPath ".env.example"
$DataDir = Join-Path $ProjectRoot "data"

# Colors for output
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "Cyan"

# ============================================
# HELPER FUNCTIONS
# ============================================

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor $ColorInfo
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor $ColorSuccess
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor $ColorWarning
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor $ColorError
}

function Test-Command {
    param([string]$CommandName)
    return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

# ============================================
# STEP 1: PRE-FLIGHT CHECKS
# ============================================

Write-Step "Running pre-flight checks..."

# Check if Docker Tools (docker CLI) is installed
if (-not (Test-Command "docker")) {
    Write-Error-Custom "Docker Tools not found. Please install Docker Tools (docker CLI) first."
    Write-Host "`nInstallation instructions:" -ForegroundColor $ColorWarning
    Write-Host "1. Install Docker Tools from: https://docs.docker.com/engine/install/" -ForegroundColor $ColorWarning
    Write-Host "2. Verify installation: docker --version" -ForegroundColor $ColorWarning
    exit 1
}

Write-Success "Docker Tools found: $(docker --version)"

# Check if Docker Compose is available
if (-not (Test-Command "docker-compose") -and -not (Test-Command "docker compose")) {
    Write-Error-Custom "Docker Compose not found. Please install Docker Compose plugin."
    exit 1
}

Write-Success "Docker Compose found"

# Check if Node.js is installed
if (-not (Test-Command "node")) {
    Write-Error-Custom "Node.js not found. Please install Node.js 18+ first."
    exit 1
}

$NodeVersion = node --version
Write-Success "Node.js found: $NodeVersion"

# Check if npm is installed
if (-not (Test-Command "npm")) {
    Write-Error-Custom "npm not found. Please install npm first."
    exit 1
}

Write-Success "npm found: $(npm --version)"

# ============================================
# STEP 2: ENVIRONMENT SETUP
# ============================================

Write-Step "Checking environment configuration..."

# Check if .env file exists
if (-not (Test-Path $EnvFile)) {
    Write-Warning ".env file not found. Creating from .env.example..."

    if (Test-Path $EnvExampleFile) {
        Copy-Item $EnvExampleFile $EnvFile
        Write-Success ".env file created. Please edit it with your configuration."
        Write-Host "`nIMPORTANT: Edit $EnvFile with your API keys before continuing." -ForegroundColor $ColorWarning
        Write-Host "Press any key to continue after editing..." -ForegroundColor $ColorWarning
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    } else {
        Write-Error-Custom ".env.example not found. Cannot create .env file."
        exit 1
    }
}

Write-Success ".env file found"

# Create data directory if it doesn't exist
if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
    Write-Success "Data directory created: $DataDir"
}

# ============================================
# STEP 3: DOCKER INFRASTRUCTURE
# ============================================

if (-not $SkipDocker) {
    Write-Step "Starting Docker infrastructure..."

    # Check if Docker daemon is running
    try {
        docker ps | Out-Null
        Write-Success "Docker daemon is running"
    } catch {
        Write-Error-Custom "Docker daemon is not running. Please start Docker Tools service."
        exit 1
    }

    # Start Docker Compose services
    Push-Location $ProjectRoot
    try {
        Write-Host "Starting PostgreSQL and Redis containers..." -ForegroundColor $ColorInfo

        # Use docker compose (modern CLI) or docker-compose (legacy)
        $ComposeCommand = if (Test-Command "docker compose") { "docker compose" } else { "docker-compose" }

        & $ComposeCommand up -d

        if ($LASTEXITCODE -ne 0) {
            Write-Error-Custom "Failed to start Docker containers"
            exit 1
        }

        Write-Success "Docker containers started successfully"

        # Wait for PostgreSQL to be ready
        Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor $ColorInfo
        $MaxAttempts = 30
        $Attempt = 0

        while ($Attempt -lt $MaxAttempts) {
            try {
                docker exec spek-postgres pg_isready -U spek_user | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "PostgreSQL is ready"
                    break
                }
            } catch {
                # Ignore errors, keep trying
            }

            $Attempt++
            Start-Sleep -Seconds 1
        }

        if ($Attempt -ge $MaxAttempts) {
            Write-Warning "PostgreSQL health check timed out (but may still work)"
        }

        # Wait for Redis to be ready
        Write-Host "Waiting for Redis to be ready..." -ForegroundColor $ColorInfo
        Start-Sleep -Seconds 2

        try {
            docker exec spek-redis redis-cli ping | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Redis is ready"
            }
        } catch {
            Write-Warning "Redis health check failed (but may still work)"
        }

    } catch {
        Write-Error-Custom "Error starting Docker infrastructure: $_"
        exit 1
    } finally {
        Pop-Location
    }
} else {
    Write-Warning "Skipping Docker startup (--SkipDocker flag set)"
}

# ============================================
# STEP 4: DATABASE MIGRATIONS
# ============================================

Write-Step "Running database migrations..."

Push-Location $AtlantisUIPath
try {
    # Check if migration runner exists
    $MigrationRunner = Join-Path $AtlantisUIPath "scripts\migrate.js"

    if (Test-Path $MigrationRunner) {
        Write-Host "Running database migrations..." -ForegroundColor $ColorInfo
        node $MigrationRunner up

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Database migrations completed"
        } else {
            Write-Warning "Database migrations failed (may need manual intervention)"
        }
    } else {
        Write-Warning "Migration runner not found at $MigrationRunner"
        Write-Host "Migrations will need to be run manually" -ForegroundColor $ColorWarning
    }
} catch {
    Write-Warning "Error running migrations: $_"
} finally {
    Pop-Location
}

# ============================================
# STEP 5: INSTALL DEPENDENCIES
# ============================================

Write-Step "Checking npm dependencies..."

Push-Location $AtlantisUIPath
try {
    # Check if node_modules exists
    $NodeModules = Join-Path $AtlantisUIPath "node_modules"

    if (-not (Test-Path $NodeModules)) {
        Write-Host "Installing npm dependencies (this may take a few minutes)..." -ForegroundColor $ColorInfo
        npm install

        if ($LASTEXITCODE -eq 0) {
            Write-Success "npm dependencies installed"
        } else {
            Write-Error-Custom "npm install failed"
            exit 1
        }
    } else {
        Write-Success "npm dependencies already installed"
    }
} finally {
    Pop-Location
}

# ============================================
# STEP 6: BUILD APPLICATION
# ============================================

Write-Step "Building Atlantis UI..."

Push-Location $AtlantisUIPath
try {
    # Check if .next directory exists (already built)
    $NextBuild = Join-Path $AtlantisUIPath ".next"

    if (-not (Test-Path $NextBuild)) {
        Write-Host "Building production bundle (this may take a few minutes)..." -ForegroundColor $ColorInfo
        npm run build

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Build completed successfully"
        } else {
            Write-Error-Custom "Build failed"
            exit 1
        }
    } else {
        Write-Success "Application already built (skipping build)"
        Write-Host "To rebuild, run: npm run build in $AtlantisUIPath" -ForegroundColor $ColorInfo
    }
} finally {
    Pop-Location
}

# ============================================
# STEP 7: START APPLICATION
# ============================================

Write-Step "Starting Atlantis UI server..."

Push-Location $AtlantisUIPath
try {
    # Start the Next.js production server
    Write-Success "Atlantis UI is starting..."
    Write-Host "`nApplication will be available at: http://localhost:3000" -ForegroundColor $ColorSuccess
    Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor $ColorWarning

    # Auto-open browser if not skipped
    if (-not $SkipBrowser) {
        Start-Sleep -Seconds 3
        Start-Process "http://localhost:3000"
    }

    # Start the server (this will block)
    npm run start

} catch {
    Write-Error-Custom "Error starting application: $_"
    exit 1
} finally {
    Pop-Location
}

# ============================================
# CLEANUP (runs on Ctrl+C)
# ============================================

Write-Step "Shutting down..."

if (-not $SkipDocker) {
    Push-Location $ProjectRoot
    try {
        Write-Host "Stopping Docker containers..." -ForegroundColor $ColorInfo
        $ComposeCommand = if (Test-Command "docker compose") { "docker compose" } else { "docker-compose" }
        & $ComposeCommand down
        Write-Success "Docker containers stopped"
    } catch {
        Write-Warning "Error stopping Docker containers: $_"
    } finally {
        Pop-Location
    }
}

Write-Success "SPEK Platform stopped successfully"
