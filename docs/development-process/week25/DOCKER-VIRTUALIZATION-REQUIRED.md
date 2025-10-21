# Docker Virtualization Configuration Required

**Date**: 2025-10-11
**Status**: ❌ BLOCKED - Hardware virtualization must be enabled in BIOS
**Priority**: P0 - Critical blocker for Week 25 deployment

---

## Current Issue

Docker Desktop is installed but cannot run because **hardware-assisted virtualization is not enabled** in the BIOS.

### System Status

```
Virtualization Enabled In Firmware: No  ❌ MUST BE "Yes"
Hyper-V Requirements:              VM Monitor Mode Extensions: Yes  ✅
Docker Desktop Installed:          Yes (v24.0.2)  ✅
Docker Desktop Process:            Running (PID 52444)  ✅
Docker Daemon Status:              Not Running  ❌
```

### Error Message

When running `docker ps`:
```
error during connect: this error may indicate that the docker daemon is not running:
Get "http://%2F%2F.%2Fpipe%2Fdocker_engine/v1.24/containers/json":
open //./pipe/docker_engine: The system cannot find the file specified.
```

**Root Cause**: Docker Desktop requires VT-x/AMD-V (hardware virtualization) to be enabled in BIOS. Without this, the Docker daemon cannot start even though the Docker Desktop application itself can launch.

---

## What You Need to Do

### Step 1: Enable Virtualization in BIOS

⚠️ **IMPORTANT**: This requires restarting your computer and entering BIOS setup.

**How to Enter BIOS**:
1. Restart your computer
2. Press the BIOS key **immediately** during boot (before Windows loads)
3. Common BIOS keys by manufacturer:
   - **Dell**: F2 or F12
   - **HP**: F10 or Esc
   - **Lenovo**: F1 or F2
   - **ASUS**: F2 or Del
   - **MSI**: Del
   - **Acer**: F2 or Del
   - **Generic/Custom PC**: Del, F2, F10, or F12

**What to Enable in BIOS**:

Look for one of these settings (name varies by manufacturer):
- **Intel CPUs**: "Intel Virtualization Technology" or "Intel VT-x" or "VT-x"
- **AMD CPUs**: "AMD-V" or "SVM Mode" (Secure Virtual Machine)

Common BIOS locations:
- **Advanced** → **CPU Configuration** → **Intel VT-x** or **AMD-V**
- **Advanced** → **Virtualization Technology**
- **Security** → **Virtualization** → **Intel VT-x**
- **System Configuration** → **Virtualization Technology**
- **Processor** → **Virtualization Technology**

**Enable the Setting**:
1. Navigate to the virtualization setting using arrow keys
2. Change from **Disabled** to **Enabled** (usually press Enter, then select Enabled)
3. Optional: Also enable "VT-d" or "IOMMU" if available (improves performance)
4. **Save and Exit** (usually F10 key, then confirm "Yes")

Your computer will restart automatically.

---

### Step 2: Enable Windows Hyper-V Features

After enabling BIOS virtualization and restarting, you must enable Windows Hyper-V features.

**Method A: PowerShell (Recommended - Fastest)**

1. Right-click **Start** → **Windows Terminal (Admin)** or **PowerShell (Admin)**
2. Run these commands:

```powershell
# Enable Hyper-V
dism.exe /Online /Enable-Feature /FeatureName:Microsoft-Hyper-V-All /All /NoRestart

# Enable Virtual Machine Platform
dism.exe /Online /Enable-Feature /FeatureName:VirtualMachinePlatform /All /NoRestart

# Enable Windows Hypervisor Platform
dism.exe /Online /Enable-Feature /FeatureName:HypervisorPlatform /All /NoRestart

# Restart computer (required!)
Restart-Computer
```

**Method B: GUI**

1. Press **Windows key** → Search "Turn Windows features on or off"
2. Check these boxes:
   - ✅ **Hyper-V** (expand and check all sub-items)
   - ✅ **Virtual Machine Platform**
   - ✅ **Windows Hypervisor Platform**
3. Click **OK**
4. Wait for Windows to download and install features (2-5 minutes)
5. **Restart** when prompted

---

### Step 3: Verify Virtualization is Enabled

After restarting from Step 2:

**Check 1: System Info**
```powershell
systeminfo | findstr /C:"Virtualization Enabled In Firmware"
```

**Expected Output**:
```
Virtualization Enabled In Firmware: Yes
```

If you see "No", go back to Step 1 and ensure you enabled the correct BIOS setting.

**Check 2: Hyper-V Status**
```powershell
systeminfo | findstr /C:"Hyper-V"
```

**Expected Output**:
```
Hyper-V Requirements:      A hypervisor has been detected. Features required for Hyper-V will not be displayed.
```

**Check 3: Task Manager**
1. Open **Task Manager** (Ctrl+Shift+Esc)
2. Go to **Performance** tab
3. Click **CPU**
4. Look at bottom right: Should say **"Virtualization: Enabled"**

---

### Step 4: Start Docker Desktop

Once virtualization is enabled and verified:

1. **Start Docker Desktop**:
   - Press Windows key → Type "Docker Desktop" → Click the application
   - Or run: `Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"`

2. **Wait for initialization** (30-90 seconds first time)

3. **Verify Docker is running**:
   ```powershell
   docker ps
   ```

   **Expected Output**:
   ```
   CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
   ```

   If you see the headers above (even with no containers), Docker is working! ✅

---

## Timeline Estimate

| Step | Time Required | Difficulty |
|------|---------------|------------|
| Enable BIOS virtualization | 5-10 minutes | Easy (if you can find the setting) |
| Enable Windows Hyper-V features | 5-10 minutes + restart | Easy |
| Docker Desktop startup | 1-2 minutes | Easy |
| **Total** | **15-25 minutes** | **Easy to Medium** |

**Note**: The hardest part is usually finding the virtualization setting in BIOS since every manufacturer organizes it differently.

---

## Troubleshooting

### "I can't find the virtualization setting in BIOS"

**Solution**:
1. Check your motherboard/computer manual
2. Google: "[Your Computer Model] enable virtualization" or "[Your Motherboard Model] enable VT-x"
3. Try these common locations:
   - Advanced → CPU Configuration
   - Advanced → Virtualization
   - Security → Virtualization
   - System Configuration → Virtualization
4. Look for keywords: "VT-x", "AMD-V", "SVM", "Virtualization Technology"

### "Virtualization is grayed out (can't change it)"

**Possible Causes**:
1. **Secure Boot is enabled**: Try disabling Secure Boot first, then enable virtualization
2. **Intel TXT is enabled**: Try disabling Intel Trusted Execution Technology (TXT) first
3. **Password protected**: Some BIOS settings require a supervisor password
4. **Not supported**: Very old CPUs (pre-2010) may not support virtualization

**Check CPU support**:
- Intel: Search "[Your CPU Model] VT-x support" on Intel's website
- AMD: Search "[Your CPU Model] AMD-V support" on AMD's website

### "Hyper-V features won't install"

**Solution**:
1. Check Windows edition: Hyper-V requires **Windows 10 Pro/Enterprise** or **Windows 11 Pro/Enterprise**
   - Windows 10 Home does NOT support Hyper-V
   - Upgrade to Pro required: https://support.microsoft.com/en-us/windows/upgrade-windows-home-to-windows-pro
2. Run Windows Update first: `Settings → Windows Update → Check for updates`
3. Try installing features via GUI method instead of PowerShell

### "Docker still won't start after enabling virtualization"

**Solution**:
1. Verify virtualization is enabled: `systeminfo | findstr /C:"Virtualization"`
2. Verify Hyper-V is running: `systeminfo | findstr /C:"Hyper-V"`
3. Reset Docker Desktop: Right-click Docker icon → Troubleshoot → Reset to factory defaults
4. Reinstall Docker Desktop: Download latest from https://www.docker.com/products/docker-desktop

---

## Why This is Required

**Docker Desktop on Windows uses one of two backends**:

1. **WSL 2 backend** (default, recommended):
   - Requires: VT-x/AMD-V + Hyper-V
   - Uses Windows Subsystem for Linux 2
   - Better performance than Hyper-V backend

2. **Hyper-V backend** (legacy):
   - Requires: VT-x/AMD-V + Hyper-V
   - Uses Windows Hyper-V virtual machines

**Both backends require hardware virtualization** because they run Linux containers inside a lightweight virtual machine. Without VT-x/AMD-V, the VM cannot start, so Docker containers cannot run.

**Why not just use Linux containers natively?**
- Windows cannot run Linux binaries directly (different kernel)
- Docker Desktop creates a Linux VM to run the containers
- The VM is lightweight (< 1 GB RAM) but still needs virtualization support

---

## Impact on Week 25 Schedule

**Original Week 25 Plan**:
- Environment Configuration: 2 hours
- Database Migration Infrastructure: 2 hours
- Staging Deployment: 4 hours
- Documentation: 2 hours
- **Total**: 10 hours

**Blocked by**: Docker virtualization configuration (~20 minutes user time)

**Updated Timeline**:
1. ✅ **Environment Configuration** - COMPLETE (`.env.example`, `docker-compose.yml`, `start-spek.ps1`)
2. ✅ **Database Migration Infrastructure** - COMPLETE (3 migrations + rollback scripts + runner)
3. ✅ **Documentation** - COMPLETE (`DESKTOP-DEPLOYMENT.md`, `ROLLBACK-PROCEDURE.md`)
4. ❌ **Testing** - BLOCKED (waiting for Docker virtualization)
5. ❌ **Staging Deployment** - BLOCKED (waiting for Docker virtualization)

**What We Can Do Without Docker**:
- ✅ Code review and documentation updates
- ✅ Test script improvements
- ✅ Performance optimization planning
- ⚠️ Cannot test containers, migrations, or full deployment

**Next Steps After Virtualization is Enabled**:
1. Start Docker Desktop (1-2 minutes)
2. Run deployment tests: `.\scripts\test-deployment.ps1` (2 minutes)
3. Start containers: `docker compose up -d` (2-5 minutes first time)
4. Run migrations: `node scripts/migrate.js up` (10 seconds)
5. Full deployment: `.\start-spek.ps1` (30-60 seconds)
6. **Total**: 5-10 minutes to complete Week 25

---

## Quick Reference Card

**Print this section and keep it handy:**

### ✅ Checklist

Before Docker Desktop will work:
- [ ] BIOS virtualization enabled (VT-x or AMD-V)
- [ ] Hyper-V Windows feature enabled
- [ ] Virtual Machine Platform enabled
- [ ] Windows Hypervisor Platform enabled
- [ ] Computer restarted after enabling features
- [ ] Verified with `systeminfo | findstr /C:"Virtualization"`

### 🔧 Quick Commands

**Check virtualization status**:
```powershell
systeminfo | findstr /C:"Virtualization Enabled In Firmware"
# Expected: "Virtualization Enabled In Firmware: Yes"
```

**Enable Hyper-V features**:
```powershell
# Run as Administrator
dism.exe /Online /Enable-Feature /FeatureName:Microsoft-Hyper-V-All /All
dism.exe /Online /Enable-Feature /FeatureName:VirtualMachinePlatform /All
dism.exe /Online /Enable-Feature /FeatureName:HypervisorPlatform /All
Restart-Computer
```

**Start Docker Desktop**:
```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
Start-Sleep -Seconds 60
docker ps
```

---

## Additional Resources

- **Docker Desktop Windows Requirements**: https://docs.docker.com/desktop/windows/install/#system-requirements
- **Enable Virtualization (Dell)**: https://www.dell.com/support/kbdoc/en-us/000124796/how-to-enable-or-disable-virtualization-on-dell-systems
- **Enable Virtualization (HP)**: https://support.hp.com/us-en/document/c03516506
- **Enable Virtualization (Lenovo)**: https://support.lenovo.com/us/en/solutions/ht500006
- **Hyper-V Documentation**: https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/

---

**Status**: WAITING FOR USER TO ENABLE BIOS VIRTUALIZATION
**Estimated Resolution Time**: 15-25 minutes
**Confidence**: 100% (this will fix the issue)

**Last Updated**: 2025-10-11
**Week**: 25 of 26
**Blocker**: Hardware virtualization not enabled in BIOS
