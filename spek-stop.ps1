# ============================================================================
# SPEK Platform Cleanup Script
# Version: 1.0.0
# Description: Safely stops all SPEK Platform services
# ============================================================================

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "SPEK Platform Cleanup"

Write-Host ""
Write-Host "🛑 Stopping SPEK Platform Services" -ForegroundColor Red
Write-Host ""

# ============================================================================
# Step 1: Stop Node.js Processes (Frontend)
# ============================================================================

Write-Host "→ Stopping Next.js frontend..." -ForegroundColor Yellow

$nodeProceses = Get-Process -Name "node" -ErrorAction SilentlyContinue

if ($nodeProceses) {
    foreach ($proc in $nodeProceses) {
        # Check if it's running on port 3000
        $connections = Get-NetTCPConnection -OwningProcess $proc.Id -ErrorAction SilentlyContinue
        $isPort3000 = $connections | Where-Object { $_.LocalPort -eq 3000 }

        if ($isPort3000) {
            Write-Host "  Stopping process $($proc.Id) (port 3000)..." -ForegroundColor Gray
            Stop-Process -Id $proc.Id -Force
        }
    }
    Write-Host "✓ Next.js frontend stopped" -ForegroundColor Green
} else {
    Write-Host "✓ No Next.js processes found" -ForegroundColor Green
}

# ============================================================================
# Step 2: Stop Python Processes (Backend)
# ============================================================================

Write-Host "→ Stopping FastAPI backend..." -ForegroundColor Yellow

$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    foreach ($proc in $pythonProcesses) {
        # Check if it's running on port 8000
        $connections = Get-NetTCPConnection -OwningProcess $proc.Id -ErrorAction SilentlyContinue
        $isPort8000 = $connections | Where-Object { $_.LocalPort -eq 8000 }

        if ($isPort8000) {
            Write-Host "  Stopping process $($proc.Id) (port 8000)..." -ForegroundColor Gray
            Stop-Process -Id $proc.Id -Force
        }
    }
    Write-Host "✓ FastAPI backend stopped" -ForegroundColor Green
} else {
    Write-Host "✓ No FastAPI processes found" -ForegroundColor Green
}

# ============================================================================
# Step 3: Stop Docker Services
# ============================================================================

Write-Host "→ Stopping Docker services (PostgreSQL + Redis)..." -ForegroundColor Yellow

try {
    docker compose down 2>&1 | Out-Null
    Write-Host "✓ Docker services stopped" -ForegroundColor Green
} catch {
    Write-Host "⚠ Docker services may already be stopped" -ForegroundColor Yellow
}

# ============================================================================
# Step 4: Verify All Services Stopped
# ============================================================================

Write-Host ""
Write-Host "→ Verifying services stopped..." -ForegroundColor Yellow

$ports = @(3000, 8000, 5432, 6379)
$allStopped = $true

foreach ($port in $ports) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue -ErrorAction SilentlyContinue

    if ($connection.TcpTestSucceeded) {
        Write-Host "  ⚠ Port $port is still in use" -ForegroundColor Yellow
        $allStopped = $false
    }
}

if ($allStopped) {
    Write-Host "✓ All services stopped successfully" -ForegroundColor Green
} else {
    Write-Host "⚠ Some services may still be running. Try running this script again." -ForegroundColor Yellow
}

# ============================================================================
# Cleanup Complete
# ============================================================================

Write-Host ""
Write-Host "👋 SPEK Platform cleanup complete" -ForegroundColor Cyan
Write-Host ""
