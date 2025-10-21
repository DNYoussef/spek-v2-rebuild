# BIOS Display Issue - Troubleshooting Guide

**Date**: 2025-10-11
**Issue**: BIOS shows only top-left corner (~1/3 of screen visible)
**System**: NVIDIA RTX 2060 SUPER, 32" Monitor, 1920x1080 @ 100% scaling

---

## Problem Description

When restarting to access BIOS, the display shows:
- ✅ POST screen appears normally (manufacturer logo)
- ❌ BIOS menu only shows **top-left corner** (~33% of screen)
- ❌ Cannot navigate to virtualization settings effectively

**Root Cause**: BIOS is outputting at a resolution/format your monitor cannot display properly (likely overscan/underscan issue or resolution mismatch).

---

## Solution 1: Monitor Auto-Adjust (EASIEST - Try First)

Your monitor likely has an "Auto-Adjust" button that can fix this immediately.

### Steps:

1. **Enter BIOS** (restart and press Del/F2/F10)
2. **When partial BIOS screen appears**, locate these physical monitor buttons:
   - Look for button labeled **"AUTO"** or **"MENU"**
   - Usually on front bottom or right side of monitor
3. **Press AUTO button** - Monitor will auto-detect and adjust
4. **Or press MENU button** → Navigate to **"Image"** or **"Display"** → Select **"Auto-Adjust"**

**Expected Result**: Screen should expand to fill properly within 2-3 seconds.

---

## Solution 2: Change Monitor Input Scaling (RECOMMENDED)

Many monitors have a "Display Area" or "Aspect Ratio" setting that causes this issue.

### Steps:

1. **Enter BIOS** (partial screen visible)
2. **Press monitor's MENU button** (physical button on monitor)
3. **Navigate using arrow buttons** to find:
   - **"Image"** or **"Display"** or **"Picture"**
   - Look for **"Display Area"** or **"Aspect Ratio"** or **"Overscan"** or **"Underscan"**
4. **Change setting**:
   - If set to **"Full"** → Change to **"1:1"** or **"Just Scan"** or **"Native"**
   - If set to **"Overscan"** → Change to **"Underscan"** or **"Off"**
   - If set to **"Auto"** → Change to **"1:1"** or **"Just Scan"**

**Common Menu Paths by Brand**:
- **Dell**: MENU → Image Settings → Display Area → 1:1
- **ASUS**: MENU → Picture → Aspect Ratio → Full
- **BenQ**: MENU → Picture → Display Mode → Full
- **LG**: MENU → Picture → Aspect Ratio → Just Scan
- **Samsung**: MENU → Picture → Picture Options → Size → Screen Fit

---

## Solution 3: Use Monitor's "Zoom" or "Position" Buttons (QUICK FIX)

Some monitors have physical buttons to adjust display positioning.

### Steps:

1. **While in BIOS** (partial screen showing)
2. **Look for monitor buttons** labeled:
   - **"Zoom -"** or **"Wide"**
   - **"H-Position"** and **"V-Position"** (horizontal/vertical position)
   - **"Resize"** or **"Size"**
3. **Press zoom/wide button** repeatedly until full screen visible
4. **Use position buttons** to center if needed

---

## Solution 4: Navigate BIOS Blind (If Monitor Can't Be Fixed)

If you can't fix the monitor display, you can still enable virtualization by navigating "blind".

### Blind Navigation Method:

**IMPORTANT**: This requires knowing your BIOS key layout. Most BIOS interfaces use:
- **Arrow keys**: Navigate menu
- **Enter**: Select item
- **F10**: Save and exit
- **Esc**: Go back

**Example: Dell BIOS (Typical Intel System)**:

```
1. Restart computer
2. Press F2 repeatedly during boot (enters BIOS)
3. Wait 3 seconds for BIOS to fully load
4. Press Right Arrow 2 times (goes to "Advanced" tab)
5. Press Enter (opens Advanced menu)
6. Press Down Arrow 3 times (highlights "Virtualization")
7. Press Enter (opens Virtualization submenu)
8. Press Down Arrow 1 time (highlights "Intel Virtualization Technology")
9. Press Enter (opens dropdown)
10. Press Up Arrow 1 time (selects "Enabled")
11. Press Enter (confirms selection)
12. Press F10 (Save and Exit)
13. Press Enter (confirm "Yes")
```

**Note**: Your BIOS layout may differ! This is just an example.

---

## Solution 5: Reset Monitor to Factory Defaults

If monitor settings are causing the issue, reset them.

### Steps:

1. **In Windows** (before restarting):
   - Press monitor's **MENU** button
   - Navigate to **"Setup"** or **"System"** or **"Settings"**
   - Select **"Reset"** or **"Factory Reset"** or **"Reset All"**
   - Confirm **"Yes"**
2. **Restart to BIOS** - Should display correctly now

---

## Solution 6: Change Windows Screen Resolution Before Restarting

Sometimes Windows resolution affects BIOS display on next boot.

### Steps:

1. **Before restarting**:
   ```powershell
   # Change Windows resolution to 1024x768 temporarily
   # Right-click Desktop → Display Settings → Resolution → 1024x768
   ```
2. **Restart to BIOS** - May display correctly at lower resolution
3. **After enabling virtualization**, change Windows resolution back to 1920x1080

---

## Solution 7: Use Different Video Cable/Port (HARDWARE)

BIOS may output differently on different ports/cables.

### If You Have Multiple Ports on Your GPU:

**Your NVIDIA RTX 2060 SUPER likely has**:
- 1x HDMI port
- 2-3x DisplayPort outputs
- Possibly 1x DVI-D port

**Try this**:
1. **Shutdown computer completely**
2. **Switch cable to different port**:
   - If currently using **HDMI** → Try **DisplayPort**
   - If currently using **DisplayPort** → Try **HDMI**
3. **Restart to BIOS** - May display correctly on different port

**Why This Works**: BIOS firmware sometimes has different default resolutions for HDMI vs DisplayPort.

---

## Solution 8: Clear CMOS (Resets BIOS Settings)

Clearing CMOS resets BIOS to factory defaults, which may fix display output.

### Method A: CMOS Battery (SAFEST)

1. **Shutdown computer completely**
2. **Unplug power cable**
3. **Open computer case**
4. **Locate CMOS battery** (coin-sized battery on motherboard, usually CR2032)
5. **Remove battery** (gently pry with flat screwdriver)
6. **Wait 5 minutes**
7. **Re-insert battery**
8. **Close case, plug in, restart**
9. **Enter BIOS** - Should display with factory defaults

### Method B: CMOS Jumper (FASTER)

1. **Shutdown computer completely**
2. **Unplug power cable**
3. **Open computer case**
4. **Locate CMOS jumper** (3-pin connector near battery, labeled "CLR_CMOS" or "JBAT1")
5. **Move jumper** from pins 1-2 to pins 2-3
6. **Wait 10 seconds**
7. **Move jumper back** to pins 1-2
8. **Close case, plug in, restart**

⚠️ **WARNING**: Clearing CMOS resets **ALL** BIOS settings to defaults (boot order, time/date, etc.)

---

## Solution 9: Update Monitor Firmware (ADVANCED)

Some monitors have firmware updates that fix display compatibility issues.

### Steps:

1. **Identify monitor model**: Check sticker on back or Windows Display Settings
2. **Google**: "[Monitor Model] firmware update"
3. **Download firmware** from manufacturer website
4. **Follow manufacturer instructions** (usually involves USB stick + monitor menu)

**Note**: This is rare and only needed if monitor is old or known to have BIOS compatibility issues.

---

## Solution 10: Use Alternative BIOS Access Methods

If you can't see BIOS to enable virtualization, use Windows methods instead.

### Method A: Enable Virtualization via Windows Settings (Some Systems)

Some OEM computers (Dell, HP, Lenovo) allow BIOS changes from Windows:

**Dell Example**:
```powershell
# Dell Command | Configure utility (if installed)
cctk --virtualization=enable
```

**HP Example**:
- HP BIOS Configuration Utility (BCU)
- Download from HP support site

**Lenovo Example**:
- Lenovo Vantage app (Microsoft Store)
- Hardware Settings → CPU → Virtualization → Enable

### Method B: Enable Hyper-V Without Entering BIOS (PARTIAL SOLUTION)

You can enable **Windows Hyper-V features** without entering BIOS:

```powershell
# Run as Administrator
dism.exe /Online /Enable-Feature /FeatureName:Microsoft-Hyper-V-All /All
dism.exe /Online /Enable-Feature /FeatureName:VirtualMachinePlatform /All
dism.exe /Online /Enable-Feature /FeatureName:HypervisorPlatform /All
Restart-Computer
```

**HOWEVER**: Docker Desktop still requires **BIOS virtualization** (VT-x/AMD-V) to be enabled. Hyper-V features alone are not sufficient.

---

## Diagnostic Questions to Help Identify Cause

Please answer these to narrow down the issue:

### 1. Monitor Connection:
- [ ] What cable are you using? (HDMI, DisplayPort, DVI, VGA)
- [ ] Is monitor connected to **motherboard** or **graphics card**? (Should be graphics card)

### 2. When Does Issue Occur:
- [ ] Does POST screen (manufacturer logo) display correctly? (Yes/No)
- [ ] Does issue ONLY happen in BIOS, or also during Windows boot? (BIOS only / Both)
- [ ] Can you see Windows login screen normally? (Yes/No)

### 3. Monitor Model:
- [ ] What is your monitor's brand and model? (Check sticker on back)
- [ ] What is monitor's native resolution? (Likely 1920x1080 or 2560x1440)

### 4. Previous Attempts:
- [ ] Have you successfully accessed BIOS on this computer before? (Yes/No)
- [ ] If yes, when did the display issue start? (After Windows update / After driver update / Always)

---

## Alternative: Use Windows Method to Enable Virtualization

If BIOS display is truly unusable, some systems allow enabling virtualization from Windows.

### Check if Your System Supports This:

```powershell
# Check manufacturer
systeminfo | findstr /C:"System Manufacturer"

# Check model
systeminfo | findstr /C:"System Model"
```

**Then Google**:
- "[Manufacturer] [Model] enable virtualization without BIOS"
- "[Manufacturer] [Model] enable VT-x from Windows"

**Known Tools**:
- **Dell**: Dell Command | Configure (CCTK)
- **HP**: HP BIOS Configuration Utility (BCU)
- **Lenovo**: Lenovo System Update / Lenovo Vantage
- **ASUS**: AI Suite (rarely supports virtualization changes)

---

## Ultimate Fallback: Use Different Computer or VM

If you absolutely cannot access BIOS to enable virtualization:

### Option A: Use Cloud Development Environment
- GitHub Codespaces (includes Docker)
- AWS Cloud9
- Google Cloud Shell

### Option B: Use WSL 2 Without Docker Desktop
- Install WSL 2: `wsl --install`
- Install Docker inside WSL 2: `sudo apt install docker.io`
- Run containers directly in WSL 2

### Option C: Use Virtual Machine (Nested Virtualization)
- Install VMware Workstation or VirtualBox
- Enable nested virtualization in VM settings
- Run Docker inside VM

**Note**: These are workarounds. Enabling BIOS virtualization is still the best solution.

---

## Recommended Action Plan

**Try solutions in this order** (easiest to hardest):

1. ✅ **Solution 1**: Monitor Auto-Adjust button (30 seconds)
2. ✅ **Solution 2**: Change monitor's Display Area setting (2 minutes)
3. ✅ **Solution 7**: Try different video port/cable (5 minutes)
4. ✅ **Solution 6**: Lower Windows resolution before restart (1 minute)
5. ⚠️ **Solution 4**: Navigate BIOS blind (requires knowing layout)
6. ⚠️ **Solution 8**: Clear CMOS (resets all BIOS settings)
7. ⚠️ **Solution 10**: Check for OEM utility to enable from Windows

---

## Quick Reference: Most Likely Fixes

**For 90% of cases, one of these three will work**:

### Fix #1: Monitor Auto-Adjust
```
1. Enter BIOS (partial screen visible)
2. Press physical "AUTO" button on monitor
3. Screen should auto-correct in 2-3 seconds
```

### Fix #2: Monitor Display Area
```
1. Enter BIOS
2. Press monitor MENU button
3. Find "Display Area" or "Aspect Ratio"
4. Change from "Full" to "1:1" or "Just Scan"
```

### Fix #3: Different Video Port
```
1. Shutdown computer
2. Move cable from HDMI to DisplayPort (or vice versa)
3. Restart to BIOS
```

---

## Post-Fix: Enabling Virtualization

Once you can see BIOS properly, enable virtualization:

### Common BIOS Paths:

**Dell**:
- Advanced → Virtualization → Intel Virtualization Technology → Enabled

**HP**:
- Configuration → Virtualization Technology → Enabled

**ASUS**:
- Advanced → CPU Configuration → Intel Virtualization Technology → Enabled

**MSI**:
- OC → CPU Features → Intel Virtualization Tech → Enabled

**Gigabyte**:
- M.I.T. → Advanced Frequency Settings → Advanced CPU Settings → SVM Mode → Enabled (AMD)
- M.I.T. → Advanced Frequency Settings → Advanced CPU Settings → Intel VT-x → Enabled (Intel)

---

## Summary

**Most Likely Cause**: Monitor's "Display Area" or "Overscan" setting is cropping BIOS output.

**Quickest Fix**: Press monitor's **AUTO button** or change **Display Area to 1:1** in monitor menu.

**If Hardware Fix Fails**: Navigate BIOS blind using arrow keys (see Solution 4).

**Last Resort**: Try to enable virtualization from Windows using OEM utility (Dell CCTK, HP BCU, etc.).

---

**Status**: TROUBLESHOOTING REQUIRED
**Estimated Fix Time**: 2-10 minutes (most cases)
**Confidence**: 90% fixable with monitor adjustments

**Last Updated**: 2025-10-11
**Related Issue**: Docker virtualization required for Week 25
