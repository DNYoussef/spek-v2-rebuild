# ============================================================================
# SPEK Platform Desktop Launcher
# Version: 1.0.0
# Description: One-click launcher for SPEK Platform v2 + Atlantis UI
# ============================================================================

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "SPEK Platform Launcher"

# ============================================================================
# Configuration
# ============================================================================
$BACKEND_PORT = 8000
$FRONTEND_PORT = 3000
$POSTGRES_PORT = 5432
$REDIS_PORT = 6379

$BACKEND_DIR = "backend"
$FRONTEND_DIR = "atlantis-ui"

# ============================================================================
# Helper Functions
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "=" * 80 -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Message)
    Write-Host "→ $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Test-Command {
    param([string]$CommandName)
    return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

function Test-Port {
    param([int]$Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
    return $connection.TcpTestSucceeded
}

function Wait-ForPort {
    param(
        [int]$Port,
        [string]$ServiceName,
        [int]$TimeoutSeconds = 30
    )

    Write-Step "Waiting for $ServiceName on port $Port..."
    $elapsed = 0

    while ($elapsed -lt $TimeoutSeconds) {
        if (Test-Port -Port $Port) {
            Write-Success "$ServiceName is ready on port $Port"
            return $true
        }
        Start-Sleep -Seconds 1
        $elapsed++
    }

    Write-Error "$ServiceName failed to start on port $Port after $TimeoutSeconds seconds"
    return $false
}

# ============================================================================
# Main Launcher
# ============================================================================

Write-Host ""
Write-Host "  ███████╗██████╗ ███████╗██╗  ██╗" -ForegroundColor Magenta
Write-Host "  ██╔════╝██╔══██╗██╔════╝██║ ██╔╝" -ForegroundColor Magenta
Write-Host "  ███████╗██████╔╝█████╗  █████╔╝ " -ForegroundColor Magenta
Write-Host "  ╚════██║██╔═══╝ ██╔══╝  ██╔═██╗ " -ForegroundColor Magenta
Write-Host "  ███████║██║     ███████╗██║  ██╗" -ForegroundColor Magenta
Write-Host "  ╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝" -ForegroundColor Magenta
Write-Host ""
Write-Host "  🤖 AI Agent Coordination Platform" -ForegroundColor Cyan
Write-Host "  Version 2.0 + Atlantis UI" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# Step 1: Check Prerequisites
# ============================================================================

Write-Header "Step 1: Checking Prerequisites"

# Check Docker Desktop
Write-Step "Checking Docker Desktop..."
if (-not (Test-Command "docker")) {
    Write-Error "Docker Desktop not found. Please install from https://www.docker.com/products/docker-desktop"
    exit 1
}

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Success "Docker Desktop is running"
} catch {
    Write-Error "Docker Desktop is not running. Please start Docker Desktop and try again."
    exit 1
}

# Check Node.js
Write-Step "Checking Node.js..."
if (-not (Test-Command "node")) {
    Write-Error "Node.js not found. Please install from https://nodejs.org/"
    exit 1
}
$nodeVersion = (node --version)
Write-Success "Node.js $nodeVersion is installed"

# Check npm
Write-Step "Checking npm..."
if (-not (Test-Command "npm")) {
    Write-Error "npm not found. Please reinstall Node.js"
    exit 1
}
$npmVersion = (npm --version)
Write-Success "npm v$npmVersion is installed"

# Check Python
Write-Step "Checking Python..."
if (-not (Test-Command "python")) {
    Write-Error "Python not found. Please install from https://www.python.org/"
    exit 1
}
$pythonVersion = (python --version)
Write-Success "$pythonVersion is installed"

# Check pip
Write-Step "Checking pip..."
if (-not (Test-Command "pip")) {
    Write-Error "pip not found. Please reinstall Python with pip"
    exit 1
}
Write-Success "pip is installed"

# ============================================================================
# Step 2: Start Docker Services
# ============================================================================

Write-Header "Step 2: Starting Docker Services (PostgreSQL + Redis)"

Write-Step "Starting Docker Compose services..."
docker compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to start Docker services"
    exit 1
}

# Wait for PostgreSQL
if (-not (Wait-ForPort -Port $POSTGRES_PORT -ServiceName "PostgreSQL" -TimeoutSeconds 30)) {
    Write-Error "PostgreSQL failed to start"
    docker compose logs postgres
    exit 1
}

# Wait for Redis
if (-not (Wait-ForPort -Port $REDIS_PORT -ServiceName "Redis" -TimeoutSeconds 30)) {
    Write-Error "Redis failed to start"
    docker compose logs redis
    exit 1
}

# ============================================================================
# Step 3: Start Backend (FastAPI)
# ============================================================================

Write-Header "Step 3: Starting Backend (FastAPI)"

Write-Step "Installing Python dependencies..."
Push-Location $BACKEND_DIR
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install Python dependencies"
    Pop-Location
    exit 1
}
Write-Success "Python dependencies installed"

Write-Step "Running database migrations..."
alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to run database migrations"
    Pop-Location
    exit 1
}
Write-Success "Database migrations completed"

Write-Step "Starting FastAPI server on port $BACKEND_PORT..."
$backendJob = Start-Job -ScriptBlock {
    param($dir, $port)
    Set-Location $dir
    uvicorn main:app --host 0.0.0.0 --port $port --reload
} -ArgumentList (Get-Location).Path, $BACKEND_PORT

Pop-Location

# Wait for backend to be ready
if (-not (Wait-ForPort -Port $BACKEND_PORT -ServiceName "FastAPI Backend" -TimeoutSeconds 30)) {
    Write-Error "FastAPI backend failed to start"
    Receive-Job -Job $backendJob
    exit 1
}

# ============================================================================
# Step 4: Start Frontend (Next.js)
# ============================================================================

Write-Header "Step 4: Starting Frontend (Next.js Atlantis UI)"

Write-Step "Installing Node.js dependencies..."
Push-Location $FRONTEND_DIR
npm install --silent
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install Node.js dependencies"
    Pop-Location
    exit 1
}
Write-Success "Node.js dependencies installed"

Write-Step "Starting Next.js development server on port $FRONTEND_PORT..."
$frontendJob = Start-Job -ScriptBlock {
    param($dir, $port)
    Set-Location $dir
    $env:PORT = $port
    npm run dev
} -ArgumentList (Get-Location).Path, $FRONTEND_PORT

Pop-Location

# Wait for frontend to be ready
if (-not (Wait-ForPort -Port $FRONTEND_PORT -ServiceName "Next.js Frontend" -TimeoutSeconds 30)) {
    Write-Error "Next.js frontend failed to start"
    Receive-Job -Job $frontendJob
    exit 1
}

# ============================================================================
# Step 5: Open Browser
# ============================================================================

Write-Header "Step 5: Opening Browser"

Start-Sleep -Seconds 2
Start-Process "http://localhost:$FRONTEND_PORT"
Write-Success "Browser opened to http://localhost:$FRONTEND_PORT"

# ============================================================================
# Startup Complete
# ============================================================================

Write-Header "🚀 SPEK Platform is Running!"

Write-Host ""
Write-Host "  📊 Services Status:" -ForegroundColor Cyan
Write-Host "  ├─ PostgreSQL:    http://localhost:$POSTGRES_PORT" -ForegroundColor White
Write-Host "  ├─ Redis:         http://localhost:$REDIS_PORT" -ForegroundColor White
Write-Host "  ├─ Backend API:   http://localhost:$BACKEND_PORT" -ForegroundColor White
Write-Host "  └─ Frontend UI:   http://localhost:$FRONTEND_PORT" -ForegroundColor White
Write-Host ""
Write-Host "  📖 API Documentation: http://localhost:$BACKEND_PORT/docs" -ForegroundColor Yellow
Write-Host "  🎨 Atlantis UI:       http://localhost:$FRONTEND_PORT" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Press Ctrl+C to stop all services" -ForegroundColor Red
Write-Host ""

# ============================================================================
# Keep Running
# ============================================================================

try {
    while ($true) {
        Start-Sleep -Seconds 1

        # Check if jobs are still running
        if ($backendJob.State -ne "Running") {
            Write-Error "Backend server stopped unexpectedly"
            Write-Host "Backend output:"
            Receive-Job -Job $backendJob
            break
        }

        if ($frontendJob.State -ne "Running") {
            Write-Error "Frontend server stopped unexpectedly"
            Write-Host "Frontend output:"
            Receive-Job -Job $frontendJob
            break
        }
    }
} catch {
    Write-Host ""
}

# ============================================================================
# Cleanup on Exit
# ============================================================================

Write-Header "Shutting Down SPEK Platform"

Write-Step "Stopping frontend server..."
Stop-Job -Job $frontendJob -ErrorAction SilentlyContinue
Remove-Job -Job $frontendJob -ErrorAction SilentlyContinue
Write-Success "Frontend stopped"

Write-Step "Stopping backend server..."
Stop-Job -Job $backendJob -ErrorAction SilentlyContinue
Remove-Job -Job $backendJob -ErrorAction SilentlyContinue
Write-Success "Backend stopped"

Write-Step "Stopping Docker services..."
docker compose down
Write-Success "Docker services stopped"

Write-Host ""
Write-Host "👋 SPEK Platform has been shut down" -ForegroundColor Cyan
Write-Host ""
