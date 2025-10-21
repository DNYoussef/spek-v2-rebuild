# SPEK Platform v2 - Deployment Test Script
# Week 25 - Comprehensive Deployment Testing
#
# This script tests all deployment components to ensure
# everything works before going to production.

param(
    [switch]$SkipDocker,
    [switch]$SkipDatabase,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$TestsPassed = 0
$TestsFailed = 0
$TestsSkipped = 0

# Colors
$ColorSuccess = "Green"
$ColorWarning = "Yellow"
$ColorError = "Red"
$ColorInfo = "Cyan"

function Write-TestResult {
    param(
        [bool]$Success,
        [string]$TestName,
        [string]$Details = ""
    )

    if ($Success) {
        Write-Host "✓ PASS: $TestName" -ForegroundColor $ColorSuccess
        $script:TestsPassed++
    } else {
        Write-Host "✗ FAIL: $TestName" -ForegroundColor $ColorError
        $script:TestsFailed++
        if ($Details) {
            Write-Host "  Error: $Details" -ForegroundColor $ColorWarning
        }
    }
}

function Write-TestSkipped {
    param([string]$TestName)
    Write-Host "⊘ SKIP: $TestName" -ForegroundColor DarkGray
    $script:TestsSkipped++
}

Write-Host "`n========================================" -ForegroundColor $ColorInfo
Write-Host "SPEK Platform Deployment Test Suite" -ForegroundColor $ColorInfo
Write-Host "========================================`n" -ForegroundColor $ColorInfo

# ============================================
# TEST 1: File Existence
# ============================================
Write-Host "TEST GROUP 1: File Existence" -ForegroundColor $ColorInfo
Write-Host "------------------------------`n" -ForegroundColor $ColorInfo

# Critical files
$files = @(
    "atlantis-ui\.env.example",
    "docker-compose.yml",
    "start-spek.ps1",
    "scripts\validate-environment.ps1",
    "atlantis-ui\prisma\migrations\001_initial_schema.sql",
    "atlantis-ui\prisma\migrations\002_add_context_dna.sql",
    "atlantis-ui\prisma\migrations\003_add_audit_logs.sql",
    "atlantis-ui\prisma\migrations\rollback\001_rollback.sql",
    "atlantis-ui\prisma\migrations\rollback\002_rollback.sql",
    "atlantis-ui\prisma\migrations\rollback\003_rollback.sql",
    "atlantis-ui\scripts\migrate.js",
    "docs\DESKTOP-DEPLOYMENT.md",
    "docs\ROLLBACK-PROCEDURE.md"
)

foreach ($file in $files) {
    $exists = Test-Path $file
    Write-TestResult -Success $exists -TestName "File exists: $file"
}

# ============================================
# TEST 2: Docker Tools Installation
# ============================================
Write-Host "`nTEST GROUP 2: Docker Tools" -ForegroundColor $ColorInfo
Write-Host "------------------------------`n" -ForegroundColor $ColorInfo

if ($SkipDocker) {
    Write-TestSkipped "Docker Tools installation (SkipDocker flag set)"
    Write-TestSkipped "Docker daemon status (SkipDocker flag set)"
    Write-TestSkipped "Docker Compose installation (SkipDocker flag set)"
} else {
    # Docker CLI
    $dockerInstalled = $null -ne (Get-Command "docker" -ErrorAction SilentlyContinue)
    Write-TestResult -Success $dockerInstalled -TestName "Docker CLI installed"

    if ($dockerInstalled) {
        # Docker daemon
        try {
            docker ps | Out-Null 2>&1
            Write-TestResult -Success $true -TestName "Docker daemon running"
        } catch {
            Write-TestResult -Success $false -TestName "Docker daemon running" -Details "Docker daemon not accessible"
        }

        # Docker Compose
        $composeInstalled = ($null -ne (Get-Command "docker-compose" -ErrorAction SilentlyContinue)) -or `
                            (docker compose version 2>&1 | Select-String "Docker Compose")
        Write-TestResult -Success $composeInstalled -TestName "Docker Compose installed"
    }
}

# ============================================
# TEST 3: Node.js Environment
# ============================================
Write-Host "`nTEST GROUP 3: Node.js Environment" -ForegroundColor $ColorInfo
Write-Host "------------------------------`n" -ForegroundColor $ColorInfo

# Node.js
$nodeInstalled = $null -ne (Get-Command "node" -ErrorAction SilentlyContinue)
Write-TestResult -Success $nodeInstalled -TestName "Node.js installed"

if ($nodeInstalled) {
    $nodeVersion = node --version
    $nodeVersionNumber = [version]($nodeVersion -replace 'v', '')
    $nodeVersionOk = $nodeVersionNumber.Major -ge 18
    Write-TestResult -Success $nodeVersionOk -TestName "Node.js version (>= 18.x)" -Details $nodeVersion
}

# npm
$npmInstalled = $null -ne (Get-Command "npm" -ErrorAction SilentlyContinue)
Write-TestResult -Success $npmInstalled -TestName "npm installed"

# ============================================
# TEST 4: Environment Configuration
# ============================================
Write-Host "`nTEST GROUP 4: Environment Configuration" -ForegroundColor $ColorInfo
Write-Host "------------------------------`n" -ForegroundColor $ColorInfo

# .env.example exists
$envExampleExists = Test-Path "atlantis-ui\.env.example"
Write-TestResult -Success $envExampleExists -TestName ".env.example exists"

# Check if .env exists (optional)
$envExists = Test-Path "atlantis-ui\.env"
if ($envExists) {
    Write-TestResult -Success $true -TestName ".env file exists"

    # Check required variables
    $envContent = Get-Content "atlantis-ui\.env" -Raw
    $requiredVars = @("DATABASE_URL", "REDIS_URL", "NODE_ENV")

    foreach ($var in $requiredVars) {
        $varSet = $envContent -match "$var\s*=\s*.+"
        Write-TestResult -Success $varSet -TestName "Environment variable: $var"
    }
} else {
    Write-Host "  ℹ .env file not found (optional, will be created on first run)" -ForegroundColor DarkGray
}

# ============================================
# TEST 5: Docker Compose Configuration
# ============================================
Write-Host "`nTEST GROUP 5: Docker Compose Configuration" -ForegroundColor $ColorInfo
Write-Host "------------------------------`n" -ForegroundColor $ColorInfo

if ($SkipDocker) {
    Write-TestSkipped "Docker Compose validation (SkipDocker flag set)"
} else {
    # Validate docker-compose.yml syntax
    try {
        $composeConfig = docker compose config 2>&1
        $configValid = $LASTEXITCODE -eq 0
        Write-TestResult -Success $configValid -TestName "Docker Compose syntax valid"
    } catch {
        Write-TestResult -Success $false -TestName "Docker Compose syntax valid" -Details $_.Exception.Message
    }
}

# ============================================
# TEST 6: Database Migration Scripts
# ============================================
Write-Host "`nTEST GROUP 6: Database Migration Scripts" -ForegroundColor $ColorInfo
Write-Host "------------------------------`n" -ForegroundColor $ColorInfo

# Check SQL syntax (basic validation)
$migrations = @(
    "atlantis-ui\prisma\migrations\001_initial_schema.sql",
    "atlantis-ui\prisma\migrations\002_add_context_dna.sql",
    "atlantis-ui\prisma\migrations\003_add_audit_logs.sql"
)

foreach ($migration in $migrations) {
    if (Test-Path $migration) {
        $content = Get-Content $migration -Raw

        # Basic SQL validation
        $hasBegin = $content -match "BEGIN;"
        $hasCommit = $content -match "COMMIT;"
        $hasValidation = $content -match "DO \$\$"

        $valid = $hasBegin -and $hasCommit -and $hasValidation
        Write-TestResult -Success $valid -TestName "Migration syntax: $(Split-Path $migration -Leaf)"

        if (-not $valid) {
            if (-not $hasBegin) { Write-Host "  Missing: BEGIN;" -ForegroundColor $ColorWarning }
            if (-not $hasCommit) { Write-Host "  Missing: COMMIT;" -ForegroundColor $ColorWarning }
            if (-not $hasValidation) { Write-Host "  Missing: Validation block" -ForegroundColor $ColorWarning }
        }
    }
}

# Check rollback scripts
$rollbacks = @(
    "atlantis-ui\prisma\migrations\rollback\001_rollback.sql",
    "atlantis-ui\prisma\migrations\rollback\002_rollback.sql",
    "atlantis-ui\prisma\migrations\rollback\003_rollback.sql"
)

foreach ($rollback in $rollbacks) {
    if (Test-Path $rollback) {
        $content = Get-Content $rollback -Raw

        # Basic SQL validation
        $hasBegin = $content -match "BEGIN;"
        $hasCommit = $content -match "COMMIT;"
        $hasValidation = $content -match "DO \$\$"

        $valid = $hasBegin -and $hasCommit -and $hasValidation
        Write-TestResult -Success $valid -TestName "Rollback syntax: $(Split-Path $rollback -Leaf)"
    }
}

# ============================================
# TEST 7: Migration Runner
# ============================================
Write-Host "`nTEST GROUP 7: Migration Runner" -ForegroundColor $ColorInfo
Write-Host "------------------------------`n" -ForegroundColor $ColorInfo

# Check migrate.js syntax
$migrateJs = "atlantis-ui\scripts\migrate.js"
if (Test-Path $migrateJs) {
    try {
        # Validate JavaScript syntax
        $validation = node --check $migrateJs 2>&1
        $syntaxValid = $LASTEXITCODE -eq 0
        Write-TestResult -Success $syntaxValid -TestName "migrate.js syntax valid"
    } catch {
        Write-TestResult -Success $false -TestName "migrate.js syntax valid" -Details $_.Exception.Message
    }

    # Check for required functions
    $content = Get-Content $migrateJs -Raw
    $hasMigrateUp = $content -match "async function migrateUp"
    $hasMigrateDown = $content -match "async function migrateDown"
    $hasShowStatus = $content -match "async function showStatus"

    Write-TestResult -Success $hasMigrateUp -TestName "migrate.js has migrateUp function"
    Write-TestResult -Success $hasMigrateDown -TestName "migrate.js has migrateDown function"
    Write-TestResult -Success $hasShowStatus -TestName "migrate.js has showStatus function"
}

# ============================================
# TEST 8: PowerShell Scripts
# ============================================
Write-Host "`nTEST GROUP 8: PowerShell Scripts" -ForegroundColor $ColorInfo
Write-Host "------------------------------`n" -ForegroundColor $ColorInfo

# start-spek.ps1
$startScript = "start-spek.ps1"
if (Test-Path $startScript) {
    try {
        $scriptContent = Get-Content $startScript -Raw
        $hasDockerCheck = $scriptContent -match "docker --version"
        $hasNodeCheck = $scriptContent -match "node --version"
        $hasMigrations = $scriptContent -match "migrate.js"

        Write-TestResult -Success $hasDockerCheck -TestName "start-spek.ps1 has Docker check"
        Write-TestResult -Success $hasNodeCheck -TestName "start-spek.ps1 has Node.js check"
        Write-TestResult -Success $hasMigrations -TestName "start-spek.ps1 runs migrations"
    } catch {
        Write-TestResult -Success $false -TestName "start-spek.ps1 validation" -Details $_.Exception.Message
    }
}

# validate-environment.ps1
$validateScript = "scripts\validate-environment.ps1"
if (Test-Path $validateScript) {
    try {
        $scriptContent = Get-Content $validateScript -Raw
        $hasDockerCheck = $scriptContent -match "docker --version"
        $hasNodeCheck = $scriptContent -match "node --version"
        $hasPortCheck = $scriptContent -match "Get-NetTCPConnection"

        Write-TestResult -Success $hasDockerCheck -TestName "validate-environment.ps1 checks Docker"
        Write-TestResult -Success $hasNodeCheck -TestName "validate-environment.ps1 checks Node.js"
        Write-TestResult -Success $hasPortCheck -TestName "validate-environment.ps1 checks ports"
    } catch {
        Write-TestResult -Success $false -TestName "validate-environment.ps1 validation" -Details $_.Exception.Message
    }
}

# ============================================
# TEST 9: Documentation
# ============================================
Write-Host "`nTEST GROUP 9: Documentation" -ForegroundColor $ColorInfo
Write-Host "------------------------------`n" -ForegroundColor $ColorInfo

# DESKTOP-DEPLOYMENT.md
$deployDoc = "docs\DESKTOP-DEPLOYMENT.md"
if (Test-Path $deployDoc) {
    $content = Get-Content $deployDoc -Raw
    $hasTOC = $content -match "## Table of Contents"
    $hasInstallation = $content -match "## Installation Steps"
    $hasTroubleshooting = $content -match "## Troubleshooting"

    Write-TestResult -Success $hasTOC -TestName "DESKTOP-DEPLOYMENT.md has TOC"
    Write-TestResult -Success $hasInstallation -TestName "DESKTOP-DEPLOYMENT.md has installation steps"
    Write-TestResult -Success $hasTroubleshooting -TestName "DESKTOP-DEPLOYMENT.md has troubleshooting"
}

# ROLLBACK-PROCEDURE.md
$rollbackDoc = "docs\ROLLBACK-PROCEDURE.md"
if (Test-Path $rollbackDoc) {
    $content = Get-Content $rollbackDoc -Raw
    $hasWhenTo = $content -match "## When to Rollback"
    $hasSteps = $content -match "## Rollback Steps"
    $hasScenarios = $content -match "## Common Scenarios"

    Write-TestResult -Success $hasWhenTo -TestName "ROLLBACK-PROCEDURE.md has trigger conditions"
    Write-TestResult -Success $hasSteps -TestName "ROLLBACK-PROCEDURE.md has rollback steps"
    Write-TestResult -Success $hasScenarios -TestName "ROLLBACK-PROCEDURE.md has common scenarios"
}

# ============================================
# TEST 10: Integration Test (If Docker Available)
# ============================================
Write-Host "`nTEST GROUP 10: Integration Test" -ForegroundColor $ColorInfo
Write-Host "------------------------------`n" -ForegroundColor $ColorInfo

if ($SkipDocker) {
    Write-TestSkipped "Docker container start (SkipDocker flag set)"
    Write-TestSkipped "PostgreSQL connectivity (SkipDocker flag set)"
    Write-TestSkipped "Redis connectivity (SkipDocker flag set)"
} else {
    # Try to start containers
    Write-Host "  Attempting to start Docker containers (this may take a moment)..." -ForegroundColor DarkGray

    try {
        $startOutput = docker compose up -d 2>&1
        $containersStarted = $LASTEXITCODE -eq 0
        Write-TestResult -Success $containersStarted -TestName "Docker containers start successfully"

        if ($containersStarted) {
            # Wait for PostgreSQL to be ready
            Start-Sleep -Seconds 5

            # Test PostgreSQL
            try {
                docker exec spek-postgres pg_isready -U spek_user 2>&1 | Out-Null
                $pgReady = $LASTEXITCODE -eq 0
                Write-TestResult -Success $pgReady -TestName "PostgreSQL is ready"
            } catch {
                Write-TestResult -Success $false -TestName "PostgreSQL is ready" -Details "Container not found or not ready"
            }

            # Test Redis
            try {
                docker exec spek-redis redis-cli ping 2>&1 | Out-Null
                $redisReady = $LASTEXITCODE -eq 0
                Write-TestResult -Success $redisReady -TestName "Redis is ready"
            } catch {
                Write-TestResult -Success $false -TestName "Redis is ready" -Details "Container not found or not ready"
            }

            # Clean up
            Write-Host "`n  Cleaning up test containers..." -ForegroundColor DarkGray
            docker compose down 2>&1 | Out-Null
        }
    } catch {
        Write-TestResult -Success $false -TestName "Docker container integration test" -Details $_.Exception.Message
    }
}

# ============================================
# FINAL SUMMARY
# ============================================
Write-Host "`n========================================" -ForegroundColor $ColorInfo
Write-Host "TEST SUMMARY" -ForegroundColor $ColorInfo
Write-Host "========================================`n" -ForegroundColor $ColorInfo

$totalTests = $TestsPassed + $TestsFailed + $TestsSkipped
$passRate = if ($totalTests -gt 0) { [math]::Round(($TestsPassed / ($TestsPassed + $TestsFailed)) * 100, 1) } else { 0 }

Write-Host "Total Tests: $totalTests" -ForegroundColor $ColorInfo
Write-Host "Passed:      $TestsPassed" -ForegroundColor $ColorSuccess
Write-Host "Failed:      $TestsFailed" -ForegroundColor $(if ($TestsFailed -gt 0) { $ColorError } else { $ColorSuccess })
Write-Host "Skipped:     $TestsSkipped" -ForegroundColor DarkGray
Write-Host "Pass Rate:   $passRate%" -ForegroundColor $(if ($passRate -ge 90) { $ColorSuccess } elseif ($passRate -ge 75) { $ColorWarning } else { $ColorError })

if ($TestsFailed -eq 0) {
    Write-Host "`n✓ ALL TESTS PASSED - READY FOR DEPLOYMENT" -ForegroundColor $ColorSuccess
    exit 0
} else {
    Write-Host "`n✗ TESTS FAILED - FIX ISSUES BEFORE DEPLOYMENT" -ForegroundColor $ColorError
    exit 1
}
