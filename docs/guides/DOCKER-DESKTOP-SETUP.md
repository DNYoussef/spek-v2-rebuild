# Docker Desktop Setup Guide

**Date**: 2025-10-11
**Status**: Docker Desktop Found - Configuration Instructions

---

## Current Status

✅ **Docker Desktop Installed**
- Location: `C:\Program Files\Docker\Docker\`
- Version: Docker 24.0.2, Compose v2.18.1
- Type: Docker Desktop (GUI application)

❌ **Hardware Virtualization Required**
- Docker Desktop requires hardware-assisted virtualization to be enabled in BIOS
- Error: "Hardware assisted virtualization and data execution protection must be enabled in the BIOS"
- **CRITICAL**: You must enable VT-x/AMD-V (or Hyper-V) in your BIOS settings before Docker Desktop will work

---

## BIOS Configuration Required

Before Docker Desktop can run, you **MUST** enable hardware virtualization in your computer's BIOS settings.

### What You Need to Enable

Depending on your CPU manufacturer:

**Intel CPUs**:
- Intel VT-x (Intel Virtualization Technology)
- Intel VT-d (optional, for device virtualization)

**AMD CPUs**:
- AMD-V (AMD Virtualization)
- SVM Mode (Secure Virtual Machine)

**Windows Features** (must also be enabled):
- Hyper-V
- Virtual Machine Platform
- Windows Hypervisor Platform

### How to Enable Virtualization in BIOS

⚠️ **WARNING**: BIOS settings vary by manufacturer. Be careful when changing BIOS settings.

⚠️ **DISPLAY ISSUE?**: If you can only see part of the BIOS screen (top-left corner, ~1/3 visible), see [BIOS-DISPLAY-FIX.md](development-process/week25/BIOS-DISPLAY-FIX.md) for solutions before proceeding.

**Step 1: Enter BIOS**
1. Restart your computer
2. Press the BIOS key during boot (usually one of these):
   - Dell: F2 or F12
   - HP: F10 or Esc
   - Lenovo: F1 or F2
   - ASUS: F2 or Del
   - MSI: Del
   - Acer: F2 or Del
   - Generic: Del, F2, F10, or F12

**Step 2: Find Virtualization Settings**

Look for these settings (location varies by BIOS):
- **Advanced** → **CPU Configuration** → **Intel VT-x** or **AMD-V**
- **Advanced** → **Virtualization Technology**
- **Security** → **Virtualization** → **Intel VT-x**
- **System Configuration** → **Virtualization Technology**

**Step 3: Enable Virtualization**
1. Find "Intel Virtualization Technology" or "AMD-V" or "SVM Mode"
2. Change from **Disabled** to **Enabled**
3. Optional: Enable "VT-d" or "IOMMU" for better performance
4. **Save and Exit** (usually F10)

**Step 4: Enable Windows Features**

After enabling BIOS virtualization, enable Windows features:

```powershell
# Run PowerShell as Administrator

# Enable Hyper-V
dism.exe /Online /Enable-Feature /FeatureName:Microsoft-Hyper-V-All /All /NoRestart

# Enable Virtual Machine Platform
dism.exe /Online /Enable-Feature /FeatureName:VirtualMachinePlatform /All /NoRestart

# Enable Windows Hypervisor Platform
dism.exe /Online /Enable-Feature /FeatureName:HypervisorPlatform /All /NoRestart

# Restart computer
Restart-Computer
```

**Or use GUI**:
1. Press Windows key → Search "Turn Windows features on or off"
2. Check these boxes:
   - ✅ Hyper-V (all sub-items)
   - ✅ Virtual Machine Platform
   - ✅ Windows Hypervisor Platform
3. Click OK
4. Restart when prompted

### Verify Virtualization is Enabled

After restarting:

```powershell
# Check if virtualization is enabled
systeminfo | findstr /C:"Virtualization Enabled In Firmware"

# Expected output:
# Virtualization Enabled In Firmware: Yes

# Check Hyper-V status
systeminfo | findstr /C:"Hyper-V"

# Expected output (if Hyper-V is running):
# Hyper-V Requirements: A hypervisor has been detected. Features required for Hyper-V will not be displayed.
```

**Alternative: Task Manager Check**
1. Open Task Manager (Ctrl+Shift+Esc)
2. Go to Performance tab
3. Click CPU
4. Look for "Virtualization: Enabled" at the bottom right

---

## Step-by-Step Setup (After Enabling Virtualization)

⚠️ **PREREQUISITE**: You MUST complete the "BIOS Configuration Required" section above before proceeding.

### Step 1: Start Docker Desktop

**Method A: Via Start Menu** (Recommended):
1. Press `Windows` key
2. Type "Docker Desktop"
3. Click on "Docker Desktop" application
4. Wait for "Docker Desktop is running" status (usually 30-60 seconds)

**Method B: Via Command Line**:
```powershell
# Start Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Wait 30 seconds
Start-Sleep -Seconds 30

# Verify it's running
docker ps
```

**Method C: Check if Already Running**:
```powershell
# Check for Docker Desktop process
Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue

# If found, Docker Desktop is running
# If not found, start it using Method A or B
```

---

### Step 2: Verify Docker Desktop is Running

**Visual Verification**:
- Look for Docker whale icon in system tray (bottom-right corner)
- Icon should be steady (not animated)
- Right-click icon → Should show "Docker Desktop is running"

**Command Line Verification**:
```powershell
# Test Docker daemon
docker ps

# Expected output: (even if empty)
CONTAINER ID   IMAGE   COMMAND   CREATED   STATUS   PORTS   NAMES

# If you see the headers above, Docker is running correctly!
```

---

### Step 3: Configure Docker Desktop Settings (Optional but Recommended)

Once Docker Desktop is running:

1. **Right-click Docker whale icon** → "Settings"

2. **General Tab**:
   - ✅ Enable "Start Docker Desktop when you log in" (for convenience)
   - ✅ Enable "Use Docker Compose V2"

3. **Resources Tab**:
   - **CPU**: Allocate at least 2 cores (4 recommended)
   - **Memory**: Allocate at least 4 GB (6-8 GB recommended for SPEK)
   - **Disk**: At least 20 GB free space

4. **Resources → WSL Integration** (if using WSL 2):
   - ✅ Enable integration with your WSL 2 distro (if applicable)

5. **Apply & Restart** if you made changes

---

### Step 4: Test Docker with SPEK Platform

Once Docker Desktop is confirmed running:

```powershell
# Navigate to project
cd C:\Users\17175\Desktop\spek-v2-rebuild

# Test Docker Compose
docker compose version

# Start SPEK containers
docker compose up -d

# Verify containers are running
docker ps

# Expected output:
CONTAINER ID   IMAGE                  STATUS       PORTS
abc123...      postgres:15-alpine     Up 5s        0.0.0.0:5432->5432/tcp
def456...      redis:7-alpine         Up 5s        0.0.0.0:6379->6379/tcp
```

---

## Troubleshooting

### Issue 0: Hardware Virtualization Not Enabled (MOST COMMON)

**Symptoms**:
- Error: "Hardware assisted virtualization and data execution protection must be enabled in the BIOS"
- Error: "The system cannot find the file specified" (when running `docker ps`)
- Docker Desktop process starts but daemon never becomes available

**Root Cause**:
Virtualization is not enabled in BIOS or Windows Hyper-V features are not enabled.

**Solution**:
See the "BIOS Configuration Required" section at the top of this document. You MUST:
1. Enable VT-x/AMD-V in BIOS
2. Enable Hyper-V Windows features
3. Restart computer
4. Then retry Docker Desktop

**Verification**:
```powershell
# Check if virtualization is enabled
systeminfo | findstr /C:"Virtualization Enabled In Firmware"
# Must show: "Virtualization Enabled In Firmware: Yes"

# Check Hyper-V is running
systeminfo | findstr /C:"Hyper-V"
# Should show: "A hypervisor has been detected"
```

### Issue 1: Docker Desktop Won't Start

**Symptoms**:
- Application opens then closes
- Error: "Docker Desktop stopped unexpectedly"

**Solutions**:
```powershell
# 1. Verify virtualization is enabled (see Issue 0 above)
systeminfo | findstr /C:"Virtualization Enabled In Firmware"

# 2. Reset Docker Desktop
Right-click Docker icon → "Troubleshoot" → "Reset to factory defaults"

# 3. Restart Windows (sometimes required after installation)
Restart-Computer

# 4. Check Windows features are enabled
# Settings → Apps → Optional Features → More Windows features
# ✅ Hyper-V (all sub-items)
# ✅ Virtual Machine Platform
# ✅ Windows Hypervisor Platform
# ✅ Windows Subsystem for Linux (if using WSL 2)
```

### Issue 2: "Docker daemon not running" after starting Docker Desktop

**Symptoms**:
- Docker Desktop shows "Starting..."
- Command `docker ps` fails

**Solutions**:
```powershell
# 1. Wait longer (Docker Desktop can take 60-90 seconds on first start)
Start-Sleep -Seconds 60
docker ps

# 2. Check Docker Desktop logs
# In Docker Desktop: Troubleshoot → View logs

# 3. Restart Docker Desktop
# Right-click Docker icon → "Restart Docker Desktop"
```

### Issue 3: Port Conflicts

**Symptoms**:
- Container fails to start
- Error: "port is already allocated"

**Solutions**:
```powershell
# Check what's using port 5432 (PostgreSQL)
netstat -ano | findstr :5432

# Check what's using port 6379 (Redis)
netstat -ano | findstr :6379

# Kill conflicting process (replace <PID> with actual process ID)
taskkill /PID <PID> /F
```

### Issue 4: WSL 2 Backend Issues

**Symptoms**:
- Error: "WSL 2 installation is incomplete"
- Docker Desktop stuck on "Starting WSL 2"

**Solutions**:
```powershell
# 1. Update WSL 2 kernel
wsl --update

# 2. Check WSL version
wsl --list --verbose

# 3. Set default WSL version to 2
wsl --set-default-version 2

# 4. Restart Docker Desktop
```

---

## Docker Desktop vs Docker Tools Clarification

**What You Have**: **Docker Desktop**
- Full Docker installation with GUI
- Includes Docker Engine + Docker Compose + Kubernetes
- Runs on Windows using WSL 2 or Hyper-V backend
- Free for personal use and small businesses
- **This is the recommended setup for Windows**

**What We Thought You Had**: "Docker Tools" (standalone CLI)
- Command-line only Docker Engine
- No GUI application
- More complex manual setup

**Conclusion**: Docker Desktop is actually **better** for your use case! It's easier to use and more reliable.

---

## Next Steps After Docker Desktop is Running

Once `docker ps` works without errors:

### 1. Create .env file
```powershell
cd C:\Users\17175\Desktop\spek-v2-rebuild\atlantis-ui
cp .env.example .env
notepad .env
```

Edit with your settings:
```env
DATABASE_URL=postgresql://spek_user:YOUR_SECURE_PASSWORD@localhost:5432/spek_db
REDIS_URL=redis://localhost:6379
NODE_ENV=production
```

### 2. Start containers
```powershell
cd ..
docker compose up -d
```

### 3. Run migrations
```powershell
cd atlantis-ui
node scripts/migrate.js up
```

### 4. Full deployment
```powershell
cd ..
.\start-spek.ps1
```

---

## Quick Reference: Docker Desktop Commands

```powershell
# Start Docker Desktop (if not auto-starting)
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Check if Docker Desktop is running
Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue

# Test Docker daemon
docker ps

# View Docker Desktop version
docker version

# View Docker Compose version
docker compose version

# Restart Docker Desktop (via system tray)
# Right-click Docker icon → "Restart Docker Desktop"

# View Docker Desktop logs
# Right-click Docker icon → "Troubleshoot" → "View logs"
```

---

## Expected Timeline

| Step | Time | Status |
|------|------|--------|
| Start Docker Desktop | 30-60 seconds | ⏳ In Progress |
| Docker daemon ready | +30 seconds | ⏳ Waiting |
| First container pull | 2-5 minutes | ⏳ Pending |
| Database migrations | 10 seconds | ⏳ Pending |
| Application start | 30 seconds | ⏳ Pending |
| **Total** | **5-7 minutes** | **From fresh start** |

---

## Confirmation Checklist

Before proceeding with SPEK deployment, confirm:

- [ ] Docker Desktop application is open
- [ ] Docker whale icon visible in system tray (steady, not animated)
- [ ] `docker ps` command works (shows container list, even if empty)
- [ ] `docker compose version` shows v2.18.1
- [ ] No error messages about "daemon not running"

Once all checked, you're ready to deploy SPEK! 🚀

---

**Last Updated**: 2025-10-11
**Docker Desktop Version**: 24.0.2
**Docker Compose Version**: v2.18.1
**Status**: Awaiting Docker Desktop startup (typical: 30-60 seconds)
