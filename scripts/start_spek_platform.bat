@echo off
REM ============================================================================
REM SPEK Platform Startup Script
REM
REM Starts all required services:
REM 1. Flask backend (port 5000)
REM 2. Atlantis UI (port 3000)
REM 3. Message monitor (optional - for debugging)
REM
REM Version: 8.2.0 (Week 26)
REM ============================================================================

echo.
echo ============================================================================
echo    SPEK Platform v2 - Atlantis UI + Claude Code Backend
echo ============================================================================
echo.
echo Starting all services...
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.9+ and try again.
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js 18+ and try again.
    pause
    exit /b 1
)

REM Check if Flask dependencies are installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Flask not installed. Installing dependencies...
    pip install flask flask-cors flask-socketio python-socketio
)

echo.
echo [1/3] Starting Flask backend (port 5000)...
echo.
start "SPEK Backend" python claude_backend_server.py

REM Wait for Flask to start
timeout /t 3 /nobreak >nul

echo.
echo [2/3] Starting Atlantis UI (port 3000)...
echo.
cd atlantis-ui
start "Atlantis UI" cmd /k "npm run dev"

REM Wait for UI to start
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Optional: Message Monitor (for debugging)
echo.
echo Press M to start message monitor, or any other key to skip...
choice /c MN /t 5 /d N /m "Start monitor? (M=Yes, N=No)"
if %errorlevel% equ 1 (
    cd ..
    start "Message Monitor" python scripts\claude_message_monitor.py
)

echo.
echo ============================================================================
echo    ALL SERVICES STARTED!
echo ============================================================================
echo.
echo Backend:  http://localhost:5000
echo UI:       http://localhost:3000
echo.
echo To stop all services: Close all terminal windows
echo.
echo ============================================================================
echo    HOW TO USE:
echo ============================================================================
echo.
echo 1. Open browser: http://localhost:3000
echo 2. Choose "New Project" or "Existing Project"
echo 3. Type your request in MonarchChat
echo 4. THIS Claude Code instance acts as Queen
echo 5. Use Task tool to spawn Princess agents
echo 6. Princess agents spawn Drones via Task tool
echo 7. Watch real-time updates in UI!
echo.
echo ============================================================================
echo.
pause
