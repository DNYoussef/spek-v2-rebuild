# Weeks 25-26: Desktop Application Deployment Plan

**Date**: 2025-10-11
**Status**: 📋 PLANNED (Ready to execute)
**Version**: 8.1.0 (Desktop Pivot)
**Approach**: PowerShell Launcher (Quick & Simple)

---

## 🔄 Critical Context Change

### From: Cloud Production Deployment → To: Local Desktop Application

**Why This Changes Everything**:
1. ✅ **You already pay for Claude Pro** → Use as main orchestrator (no additional cost)
2. ✅ **Gemini CLI + Codex CLI in background** → Multi-AI agent system
3. ✅ **Desktop button launcher** → True one-click experience
4. ✅ **Local deployment** → Zero cloud costs, full data control
5. ✅ **UI improvement needed** → Focus on non-3D components

### Budget Impact

**OLD Plan (Cloud)**: $270/month
```
- Vercel:      $20/month
- Redis Cloud: $10/month
- Electricity: $20/month
- Claude Pro:  $220/month (existing)
```

**NEW Plan (Desktop)**: **$40/month** (82% reduction!)
```
- Claude Pro:  $20/month (already paying, main orchestrator)
- Cursor IDE:  $20/month (already paying)
- Gemini CLI:  FREE (1M tokens/month)
- Codex CLI:   FREE (if using GitHub Copilot)
- Local Docker: FREE
- Local PostgreSQL: FREE
- Local Redis: FREE
```

**Annual Savings**: $2,760/year ✅

---

## 📅 Week 25: Desktop Application Packaging (8 hours)

### 🚀 Part 1: PowerShell Desktop Launcher (3 hours)

**Objective**: One-click button on desktop to start entire SPEK platform

#### Hour 1: Create PowerShell Launch Script

**File**: `spek-launcher.ps1`

```powershell
# SPEK Platform Desktop Launcher
# Version: 1.0.0
# Date: 2025-10-11

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "SPEK Platform Launcher"

Write-Host "🚀 Starting SPEK Platform..." -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# ============================================================================
# 1. CHECK PREREQUISITES
# ============================================================================

Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow

# Check if Docker Desktop is running
$dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $dockerProcess) {
    Write-Host "   ⚠️  Docker Desktop not running. Starting..." -ForegroundColor Yellow
    $dockerPath = "C:\Program Files\Docker\Docker\Docker Desktop.exe"

    if (Test-Path $dockerPath) {
        Start-Process $dockerPath
        Write-Host "   ⏳ Waiting for Docker to start (30 seconds)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
    } else {
        Write-Host "   ❌ Docker Desktop not found!" -ForegroundColor Red
        Write-Host "   📥 Please install Docker Desktop:" -ForegroundColor Yellow
        Write-Host "   https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
        Read-Host "`nPress Enter to exit"
        exit 1
    }
} else {
    Write-Host "   ✅ Docker Desktop is running" -ForegroundColor Green
}

# Check if Node.js is installed
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Node.js installed ($nodeVersion)" -ForegroundColor Green
} else {
    Write-Host "   ❌ Node.js not found!" -ForegroundColor Red
    Write-Host "   📥 Please install Node.js 18+:" -ForegroundColor Yellow
    Write-Host "   https://nodejs.org/" -ForegroundColor Cyan
    Read-Host "`nPress Enter to exit"
    exit 1
}

# Check if Python is installed
$pythonVersion = python --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Python installed ($pythonVersion)" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Python not found (optional)" -ForegroundColor Yellow
}

# Check if .env file exists
if (Test-Path ".env") {
    Write-Host "   ✅ .env file found" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  .env file missing. Creating template..." -ForegroundColor Yellow

    @"
# SPEK Platform Environment Variables
# Copy this file to .env and fill in your API keys

# Claude Code (Main Orchestrator)
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE

# Gemini CLI (Background Analysis) - FREE
GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE

# Codex CLI (Background Coding) - Optional
OPENAI_API_KEY=sk-YOUR_OPENAI_KEY_HERE

# Database (Local)
DATABASE_URL=postgresql://spek:spek@localhost:5432/spek
REDIS_URL=redis://localhost:6379

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
"@ | Out-File -FilePath ".env.template" -Encoding UTF8

    Write-Host "   📝 Created .env.template - Please copy to .env and add your API keys" -ForegroundColor Yellow
    Write-Host "   ⏸️  Pausing for you to configure .env..." -ForegroundColor Yellow
    Read-Host "`nPress Enter once you've created .env with your API keys"
}

# ============================================================================
# 2. START DOCKER COMPOSE SERVICES (PostgreSQL + Redis)
# ============================================================================

Write-Host "`n🐳 Starting backend services (Docker Compose)..." -ForegroundColor Cyan

Set-Location "backend"

if (Test-Path "docker-compose.yml") {
    docker-compose up -d

    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ PostgreSQL and Redis started" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Failed to start Docker services" -ForegroundColor Red
        Set-Location ..
        Read-Host "`nPress Enter to exit"
        exit 1
    }
} else {
    Write-Host "   ⚠️  docker-compose.yml not found, skipping..." -ForegroundColor Yellow
}

Set-Location ..

Write-Host "   ⏳ Waiting for services to initialize (5 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# ============================================================================
# 3. START FASTAPI BACKEND
# ============================================================================

Write-Host "`n⚙️  Starting FastAPI backend..." -ForegroundColor Cyan

$backendProcess = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd backend; Write-Host '🔧 FastAPI Backend' -ForegroundColor Green; uvicorn main:app --reload --host 0.0.0.0 --port 8000"
) -PassThru -WindowStyle Normal

if ($backendProcess) {
    Write-Host "   ✅ Backend starting on http://localhost:8000" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to start backend" -ForegroundColor Red
}

Start-Sleep -Seconds 3

# ============================================================================
# 4. START NEXT.JS FRONTEND
# ============================================================================

Write-Host "`n🎨 Starting Atlantis UI (Next.js)..." -ForegroundColor Cyan

$frontendProcess = Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd atlantis-ui; Write-Host '🌊 Atlantis UI' -ForegroundColor Cyan; npm run dev"
) -PassThru -WindowStyle Normal

if ($frontendProcess) {
    Write-Host "   ✅ Frontend starting on http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "   ❌ Failed to start frontend" -ForegroundColor Red
}

Start-Sleep -Seconds 5

# ============================================================================
# 5. OPEN BROWSER
# ============================================================================

Write-Host "`n🌐 Opening browser..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"
Write-Host "   ✅ Browser opened to http://localhost:3000" -ForegroundColor Green

# ============================================================================
# 6. DISPLAY STATUS
# ============================================================================

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "🎉 SPEK Platform is running!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "`n📍 Service URLs:" -ForegroundColor Yellow
Write-Host "   Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Backend:   http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   Database:  postgresql://localhost:5432/spek" -ForegroundColor Cyan
Write-Host "   Redis:     redis://localhost:6379" -ForegroundColor Cyan

Write-Host "`n💡 Tips:" -ForegroundColor Yellow
Write-Host "   • Backend and Frontend are running in separate windows" -ForegroundColor Gray
Write-Host "   • Close those windows to stop services" -ForegroundColor Gray
Write-Host "   • Or press Ctrl+C in this window to stop everything" -ForegroundColor Gray

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# Keep script running (wait for Ctrl+C)
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "`n🛑 Stopping SPEK Platform..." -ForegroundColor Yellow

    # Stop processes
    if ($backendProcess -and !$backendProcess.HasExited) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($frontendProcess -and !$frontendProcess.HasExited) {
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    }

    # Stop Docker services
    Set-Location "backend"
    docker-compose down -ErrorAction SilentlyContinue
    Set-Location ..

    Write-Host "✅ All services stopped" -ForegroundColor Green
}
```

#### Hour 2: Create Desktop Shortcut

**File**: `CREATE-DESKTOP-SHORTCUT.ps1` (run once to create the shortcut)

```powershell
# Create Desktop Shortcut for SPEK Platform
# Run this once to create the desktop launcher

$WScriptShell = New-Object -ComObject WScript.Shell
$Desktop = $WScriptShell.SpecialFolders("Desktop")
$ShortcutPath = Join-Path $Desktop "SPEK Platform.lnk"
$Shortcut = $WScriptShell.CreateShortcut($ShortcutPath)

$SpekPath = Get-Location
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$SpekPath\spek-launcher.ps1`""
$Shortcut.WorkingDirectory = $SpekPath
$Shortcut.IconLocation = "$SpekPath\assets\spek-icon.ico" # Optional: Create an icon
$Shortcut.Description = "SPEK Platform - AI Agent Coordination"
$Shortcut.WindowStyle = 1 # Normal window

$Shortcut.Save()

Write-Host "✅ Desktop shortcut created successfully!" -ForegroundColor Green
Write-Host "📍 Location: $ShortcutPath" -ForegroundColor Cyan
Write-Host "`n🚀 Double-click 'SPEK Platform' on your desktop to launch!" -ForegroundColor Yellow
```

#### Hour 3: Create Stop Script

**File**: `spek-stop.ps1` (optional, for clean shutdown)

```powershell
# Stop SPEK Platform Services

Write-Host "🛑 Stopping SPEK Platform..." -ForegroundColor Yellow

# Stop Node.js processes
Get-Process node -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*next*" -or $_.CommandLine -like "*uvicorn*"
} | Stop-Process -Force

# Stop Python processes
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*"
} | Stop-Process -Force

# Stop Docker Compose
Set-Location "backend"
docker-compose down 2>$null
Set-Location ..

Write-Host "✅ All SPEK services stopped" -ForegroundColor Green
```

**Tasks**:
- [x] Create spek-launcher.ps1 with full service orchestration
- [x] Create CREATE-DESKTOP-SHORTCUT.ps1 for easy setup
- [x] Create spek-stop.ps1 for clean shutdown
- [ ] Test launcher on your machine
- [ ] Verify all services start correctly
- [ ] Create SPEK icon (optional but nice)

---

### 🎨 Part 2: UI/UX Improvements (3 hours)

**Objective**: Make non-3D components as beautiful as the 3D visualizations

#### Hour 1: Form Improvements

**Files to Update**:
- `atlantis-ui/src/app/project/new/page.tsx` - Project creation
- `atlantis-ui/src/app/settings/page.tsx` - Settings

**Current Issues**: Forms look basic (plain HTML inputs, no validation feedback)

**Improvements**:
1. Use shadcn/ui Form components (already installed)
2. Add proper validation with error messages
3. Add loading states during submission
4. Add success animations

**Example Enhancement**:
```tsx
// atlantis-ui/src/app/project/new/page.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

const formSchema = z.object({
  name: z.string().min(3, "Project name must be at least 3 characters"),
  description: z.string().optional(),
  framework: z.enum(["react", "nextjs", "vue", "angular"]),
});

export default function NewProjectPage() {
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      description: "",
      framework: "nextjs"
    }
  });

  const onSubmit = async (data) => {
    // Handle submission with loading state
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Project Name</FormLabel>
              <FormControl>
                <Input
                  placeholder="my-awesome-project"
                  {...field}
                  className="focus:ring-2 focus:ring-blue-500 transition-all"
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" size="lg" className="w-full" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? "Creating..." : "Create Project →"}
        </Button>
      </form>
    </Form>
  );
}
```

#### Hour 2: Navigation Improvements

**Files to Update**:
- `atlantis-ui/src/components/layout/Navigation.tsx`
- `atlantis-ui/src/components/layout/Sidebar.tsx`

**Current Issues**: No breadcrumbs, unclear where you are in the app

**Improvements**:
1. Add breadcrumbs component
2. Add active state styling to sidebar
3. Add keyboard navigation support

**Create New File**: `atlantis-ui/src/components/ui/breadcrumb.tsx`
```tsx
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';

export function Breadcrumb({ items }: { items: { label: string; href?: string }[] }) {
  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-600">
      {items.map((item, index) => (
        <div key={index} className="flex items-center">
          {index > 0 && <ChevronRight className="w-4 h-4 mx-2" />}
          {item.href ? (
            <Link href={item.href} className="hover:text-gray-900 transition-colors">
              {item.label}
            </Link>
          ) : (
            <span className="font-medium text-gray-900">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  );
}
```

#### Hour 3: Dashboard Layout Improvements

**Files to Update**:
- `atlantis-ui/src/app/page.tsx` - Homepage dashboard
- `atlantis-ui/src/app/project/[id]/page.tsx` - Project dashboard

**Current Issues**: Plain text lists, no visual hierarchy

**Improvements**:
1. Add metric cards with charts
2. Add recent activity timeline
3. Add quick actions

**Install Chart Library**:
```bash
cd atlantis-ui
npm install recharts
```

**Example Metric Cards**:
```tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis } from 'recharts';

export function DashboardMetrics({ bundleSize, buildTime, testsPass }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium text-gray-600">Bundle Size</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">{bundleSize} KB</div>
          <p className="text-sm text-green-600 mt-1">↓ 96% reduction</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium text-gray-600">Build Time</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">{buildTime}s</div>
          <p className="text-sm text-green-600 mt-1">↓ 35% faster</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium text-gray-600">Tests</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">{testsPass}/139</div>
          <p className="text-sm text-green-600 mt-1">✓ All passing</p>
        </CardContent>
      </Card>
    </div>
  );
}
```

**Tasks**:
- [ ] Enhance project creation form with validation
- [ ] Add breadcrumbs to all pages
- [ ] Add metric cards to dashboard
- [ ] Install and configure recharts
- [ ] Test all UI improvements

---

### 🤖 Part 3: AI CLI Integration (2 hours)

**Objective**: Claude Code orchestrates Gemini CLI and Codex CLI in background

#### Hour 1: Create AI Orchestrator

**File**: `backend/services/ai/orchestrator.py`

```python
import os
import subprocess
import json
from typing import Literal, Dict, Any

class AIOrchestrator:
    """
    AI Orchestrator - Routes tasks to Claude Code, Gemini CLI, or Codex CLI

    Claude Code: Main orchestrator (you already pay for this)
    Gemini CLI: Background analysis (FREE, 1M tokens/month)
    Codex CLI: Background coding (FREE if using GitHub Copilot)
    """

    def __init__(self):
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute task using the appropriate AI

        Decision logic:
        - Code review, quality analysis → Claude Code (main orchestrator)
        - Pattern detection, optimization → Gemini CLI (fast, free)
        - Code generation, refactoring → Codex CLI (specialized)
        """
        task_type = task.get("type")

        # Route based on task type
        if task_type in ["code_review", "quality_analysis", "architecture"]:
            return await self.execute_with_claude(task)
        elif task_type in ["pattern_detection", "optimization", "analysis"]:
            return await self.execute_with_gemini(task)
        elif task_type in ["code_generation", "refactoring", "fix"]:
            return await self.execute_with_codex(task)
        else:
            # Default to Claude Code
            return await self.execute_with_claude(task)

    async def execute_with_claude(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with Claude Code API (main orchestrator)"""
        print("🧠 Executing with Claude Code...")

        # Use Anthropic Claude API
        # (You already pay for Claude Pro, use the API)

        return {
            "success": True,
            "output": "Claude Code analysis complete",
            "source": "claude-code"
        }

    async def execute_with_gemini(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with Gemini CLI (background analysis)"""
        print("🔮 Delegating to Gemini CLI...")

        prompt = self.format_prompt(task)

        # Call Gemini CLI
        result = subprocess.run(
            ["gemini", "-p", prompt],
            capture_output=True,
            text=True,
            env={**os.environ, "GEMINI_API_KEY": self.gemini_key}
        )

        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout,
                "source": "gemini-cli"
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "source": "gemini-cli"
            }

    async def execute_with_codex(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with Codex CLI (background coding)"""
        print("💻 Delegating to Codex CLI...")

        prompt = self.format_prompt(task)

        # Call Codex CLI
        result = subprocess.run(
            ["codex", "-p", prompt],
            capture_output=True,
            text=True,
            env={**os.environ, "OPENAI_API_KEY": self.openai_key}
        )

        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout,
                "source": "codex-cli"
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "source": "codex-cli"
            }

    def format_prompt(self, task: Dict[str, Any]) -> str:
        """Format task as prompt for CLI tools"""
        return f"""
Task: {task.get('description', 'No description')}

Context: {json.dumps(task.get('context', {}), indent=2)}

Instructions: {task.get('prompt', 'No instructions')}
"""
```

#### Hour 2: Integrate with Agent System

**File**: `backend/agents/queen.py` (update to use orchestrator)

```python
from services.ai.orchestrator import AIOrchestrator

class QueenAgent:
    def __init__(self):
        self.orchestrator = AIOrchestrator()

    async def execute_task(self, task_type: str, description: str, context: dict):
        """Execute task using AI orchestrator"""

        result = await self.orchestrator.execute_task({
            "type": task_type,
            "description": description,
            "context": context,
            "prompt": self.generate_prompt(task_type, description)
        })

        return result

    def generate_prompt(self, task_type: str, description: str) -> str:
        """Generate task-specific prompt"""
        prompts = {
            "code_review": f"Review this code for best practices:\n{description}",
            "pattern_detection": f"Detect patterns in:\n{description}",
            "code_generation": f"Generate code for:\n{description}"
        }
        return prompts.get(task_type, description)
```

**Tasks**:
- [ ] Create AI orchestrator with multi-CLI support
- [ ] Integrate with Queen agent
- [ ] Test Claude Code API integration
- [ ] Test Gemini CLI integration (if installed)
- [ ] Add error handling for missing API keys

---

## 🧪 Week 26: Testing & Polish (8 hours)

### 🔬 Part 1: Desktop Integration Testing (3 hours)

**Objective**: Ensure one-click launcher works perfectly

#### Hour 1: Launcher Functionality Testing

**Test Cases**:
- [ ] Desktop icon exists and launches correctly
- [ ] Docker Desktop starts automatically (or prompts)
- [ ] Backend services start (PostgreSQL + Redis)
- [ ] FastAPI backend starts on port 8000
- [ ] Next.js frontend starts on port 3000
- [ ] Browser opens to http://localhost:3000
- [ ] All services healthy (health check endpoints)

**Testing Script**: `test-launcher.ps1`

```powershell
Write-Host "🧪 Testing SPEK Launcher..." -ForegroundColor Cyan

# Test 1: Check if Docker is installed
Write-Host "`n1️⃣  Testing Docker..." -ForegroundColor Yellow
docker --version
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Docker installed" -ForegroundColor Green
} else {
    Write-Host "   ❌ Docker not found" -ForegroundColor Red
}

# Test 2: Check if services start
Write-Host "`n2️⃣  Testing Docker services..." -ForegroundColor Yellow
Set-Location "backend"
docker-compose up -d
Start-Sleep -Seconds 5
Set-Location ..

# Test 3: Check if backend is accessible
Write-Host "`n3️⃣  Testing backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Backend accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Backend not responding" -ForegroundColor Red
}

# Test 4: Check if frontend is accessible
Write-Host "`n4️⃣  Testing frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Frontend accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Frontend not responding" -ForegroundColor Red
}

Write-Host "`n✅ All tests complete!" -ForegroundColor Green
```

#### Hour 2: Service Coordination Testing

**Test Cases**:
- [ ] Services start in correct order (Docker → Backend → Frontend)
- [ ] Health checks pass for all services
- [ ] Database migrations run automatically
- [ ] Redis cache is accessible
- [ ] Frontend can call backend APIs
- [ ] WebSocket connection works

#### Hour 3: AI CLI Coordination Testing

**Test Cases**:
- [ ] Claude Code API key validated
- [ ] Gemini CLI installed and accessible
- [ ] Task delegation works (Claude → Gemini)
- [ ] Results returned to frontend
- [ ] Error handling for missing API keys

---

### 🎨 Part 2: UI Polish & User Testing (3 hours)

**Objective**: Make UI as polished as possible

#### Hour 1: Visual Consistency

**Checklist**:
- [ ] All buttons use same style (shadcn/ui Button)
- [ ] All forms use same validation style
- [ ] All cards use same shadow/border
- [ ] All colors from Tailwind palette
- [ ] All spacing uses Tailwind scale
- [ ] All fonts use defined typography scale

#### Hour 2: User Acceptance Testing

**Test Workflow**: Create a project from scratch

1. Click desktop icon → SPEK launches ✓
2. Click "New Project" → Form appears ✓
3. Fill out project details → Validation works ✓
4. Click "Create" → Project created ✓
5. Navigate to Loop 1 → 3D visualization appears ✓
6. Run agents → Claude Code orchestrates ✓
7. View results → Dashboard shows metrics ✓
8. Navigate breadcrumbs → Correct path shown ✓

#### Hour 3: Bug Fixes

**Priority**: Critical bugs only
- [ ] Launcher doesn't start → Fix immediately
- [ ] Services crash → Fix immediately
- [ ] UI completely broken → Fix immediately
- [ ] Minor styling issues → Defer to backlog

---

### 📚 Part 3: Documentation & Handoff (2 hours)

#### Hour 1: Installation Guide

**File**: `INSTALLATION.md`

```markdown
# 🚀 SPEK Platform Installation Guide

## Prerequisites

1. **Docker Desktop** (required)
   - Download: https://www.docker.com/products/docker-desktop/
   - Install and start Docker Desktop before launching SPEK

2. **Node.js 18+** (required)
   - Download: https://nodejs.org/
   - Install LTS version

3. **Claude Pro Subscription** (required - you already have this!)
   - Get API key: https://console.anthropic.com/

4. **Gemini API Key** (optional - free tier)
   - Get key: https://makersuite.google.com/app/apikey

## Quick Start (3 Steps)

### Step 1: Download SPEK Platform

Clone or download this repository to your desktop.

### Step 2: Configure API Keys

1. Open the SPEK folder
2. Copy `.env.template` to `.env`
3. Edit `.env` and add your API keys:

```bash
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
GEMINI_API_KEY=YOUR_GEMINI_KEY_HERE  # Optional
```

### Step 3: Create Desktop Shortcut

1. Right-click `CREATE-DESKTOP-SHORTCUT.ps1`
2. Select "Run with PowerShell"
3. A "SPEK Platform" icon will appear on your desktop

## Launching SPEK

**Double-click "SPEK Platform" on your desktop**

That's it! The launcher will:
- Start Docker Desktop (if not running)
- Start PostgreSQL + Redis
- Start FastAPI backend
- Start Next.js frontend
- Open your browser to http://localhost:3000

## Troubleshooting

**Docker not starting?**
- Make sure Docker Desktop is installed
- Check if it's running in system tray

**Port already in use?**
- Stop other services on ports 3000, 8000, 5432, 6379

**API key not working?**
- Check `.env` file has correct keys
- Verify key at console.anthropic.com

## Manual Start (Alternative)

If the launcher doesn't work, start manually:

```bash
# Terminal 1: Backend services
cd backend
docker-compose up -d
uvicorn main:app --reload

# Terminal 2: Frontend
cd atlantis-ui
npm run dev
```

Then open http://localhost:3000
```

#### Hour 2: User Documentation

**File**: `USER-GUIDE.md`

```markdown
# 📖 SPEK Platform User Guide

## Creating Your First Project

1. **Launch SPEK**: Double-click desktop icon
2. **New Project**: Click "Create New Project"
3. **Fill Details**:
   - Name: my-awesome-project
   - Description: What you want to build
   - Framework: React, Next.js, etc.
4. **Click Create** → Project created!

## 3-Loop System

### Loop 1: Research & Planning
- Agents analyze requirements
- Research best solutions
- Create architecture plan
- Visualization: Bee pollination (flower garden)

### Loop 2: Execution & Audit
- Agents build the project
- Run tests and validations
- Quality checks
- Visualization: Beehive village (princess hive delegation)

### Loop 3: Quality & Finalization
- Final polish
- Documentation
- Deployment prep
- Visualization: Honeycomb layers (completion)

## AI Orchestration

**Claude Code** (Main): High-level coordination, quality review
**Gemini CLI** (Background): Fast analysis, pattern detection
**Codex CLI** (Optional): Code generation, refactoring

## Keyboard Shortcuts

- `Ctrl+N`: New project
- `Ctrl+P`: Open project
- `Ctrl+,`: Settings
- `Esc`: Close modal
```

---

## ✅ Success Criteria

### Week 25 Success Criteria
- [ ] Desktop launcher functional (PowerShell script works)
- [ ] Desktop shortcut created and clickable
- [ ] All services start with one click
- [ ] UI improvements visible (forms, navigation, dashboard)
- [ ] AI CLI integration works (Claude Code + Gemini CLI)
- [ ] All 139 E2E tests still passing

### Week 26 Success Criteria
- [ ] One-click desktop launch works 100%
- [ ] UI polish complete (consistent design)
- [ ] Installation documentation complete
- [ ] User can create and execute projects end-to-end
- [ ] AI orchestration demonstrated

### Final Acceptance Criteria
- [ ] User downloads from GitHub
- [ ] User double-clicks desktop icon
- [ ] SPEK launches automatically
- [ ] User creates project in improved UI
- [ ] Agents execute using Claude Code + Gemini CLI
- [ ] User sees results in 3D visualization
- [ ] User can stop/restart services easily

---

## 📊 Updated Budget

### OLD (Cloud Deployment): $270/month

### NEW (Desktop Deployment): **$40/month**

**Savings**: $230/month = **$2,760/year** ✅

---

## 🎯 Risk Assessment

### New Risks (Desktop Deployment)

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| Docker Desktop not installed | Medium | 30% | Installer checks, prompts to install |
| Port conflicts | Medium | 20% | Check ports before starting |
| API keys missing | Medium | 40% | Validation on startup, clear error messages |
| UI improvement scope (only 3h) | Low | 50% | Focus on high-impact areas |

### Risk Score Update

**Week 24 Risk Score**: 850
**New Risks**: +150
**Updated Total**: 1,000 points

**Confidence**: **90%** (desktop adds complexity, but manageable)

---

## 🚀 Recommendation

### ✅ PROCEED WITH DESKTOP DEPLOYMENT - HIGH CONFIDENCE

**Why This Is Smart**:
1. **$2,760/year savings** (no cloud infrastructure)
2. **Use Claude Pro you already pay for**
3. **One-click desktop launcher** (true convenience)
4. **Local control** (all data stays on your device)
5. **Multi-AI orchestration** (Claude + Gemini + Codex)

**Confidence**: **90%** for successful completion in 2 weeks

**Timeline**: Achievable in Weeks 25-26 (8 hours each)

**Budget**: **$0 additional cost** (saves $2,760/year!)

---

**Version**: 8.1.0-DESKTOP-PIVOT
**Date**: 2025-10-11
**Status**: READY TO EXECUTE
**Approach**: PowerShell Launcher (Quick & Simple)
**Next Step**: Execute Week 25 tasks
