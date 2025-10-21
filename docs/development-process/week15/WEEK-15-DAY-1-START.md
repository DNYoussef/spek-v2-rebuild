# Week 15 Day 1 - Playwright Configuration & Visual Testing Setup

**Date**: 2025-10-09
**Status**: 🔄 IN PROGRESS
**Week**: 15 of 26 (UI Validation + Polish)
**Day**: 1 of 7
**Focus**: Playwright configuration, visual testing infrastructure, UI verification

---

## Day 1 Objectives

### Primary Goals
1. ✅ Configure Playwright with proper timeout settings (30s + exponential backoff)
2. ✅ Install Playwright browsers (Chromium for visual testing)
3. ✅ Create comprehensive E2E test suite for all pages
4. ✅ Implement screenshot capture system with dynamic content masking
5. ✅ Test all 9 Atlantis UI pages with visual regression

### Success Criteria
- [ ] Playwright configured with 30s timeout
- [ ] Chromium browser installed successfully
- [ ] All 9 pages load without errors
- [ ] Screenshots captured for visual baseline
- [ ] Dynamic content (timestamps, avatars) properly masked
- [ ] False positive rate <10%

---

## Current Status

### Servers Running ✅
- **Frontend**: http://localhost:3002 (Next.js 15.5.4 with Turbopack)
- **Backend**: http://localhost:3001 (tRPC + WebSocket + Socket.io)
- **Health Check**: `{"status":"ok","timestamp":"2025-10-09T15:00:27.456Z","services":{"trpc":"ready","websocket":"ready"}}`

### Existing Test Infrastructure (from Week 14)
- `playwright.config.ts` - Basic configuration (needs 30s timeout update)
- `tests/e2e/homepage.spec.ts` - Homepage test (3 test cases)
- `tests/e2e/loop-visualizers.spec.ts` - Loop pages test (5 test cases)
- **Total**: 8 existing E2E tests

### Pages to Test (9 total)
1. `/` - Homepage (Monarch Chat) ✅
2. `/project/select` - Existing Project Selector
3. `/project/new` - New Project Wizard
4. `/loop1` - Research & Pre-mortem ✅
5. `/loop2` - Execution Village ✅
6. `/loop2/audit` - 3-Stage Audit Pipeline
7. `/loop2/ui-review` - UI Validation
8. `/loop3` - Quality & Finalization ✅
9. `/dashboard` - Overall Progress

---

## Implementation Plan

### Task 1: Update Playwright Configuration (30 minutes)
**Objective**: Configure Playwright with research-backed settings

**Changes Needed**:
1. Increase timeout from 5s default to 30s (for 3D/WebGL pages)
2. Add exponential backoff retry logic (5s, 10s, 30s)
3. Configure dynamic content masking
4. Add animation disabling (prevent mid-animation captures)
5. Set screenshot tolerance threshold (1% maxDiffPixelRatio)

**Files to Modify**:
- `atlantis-ui/playwright.config.ts`

### Task 2: Install Playwright Browsers (15 minutes)
**Objective**: Install Chromium browser for testing

**Command**:
```bash
cd atlantis-ui
npx playwright install chromium
```

### Task 3: Create Comprehensive E2E Tests (2 hours)
**Objective**: Test all 9 pages with screenshot capture

**Test Files to Create**:
1. `tests/e2e/project-pages.spec.ts` - Project selector + wizard
2. `tests/e2e/loop2-audit.spec.ts` - Audit pipeline page
3. `tests/e2e/loop2-ui-review.spec.ts` - UI review page
4. `tests/e2e/dashboard.spec.ts` - Dashboard page

**Existing Tests to Update**:
- `tests/e2e/homepage.spec.ts` - Add screenshot masking
- `tests/e2e/loop-visualizers.spec.ts` - Add 30s timeout for 3D rendering

### Task 4: Implement Screenshot Masking (1 hour)
**Objective**: Mask dynamic content to prevent false positives

**Dynamic Content to Mask**:
- Timestamps (`[data-testid="timestamp"]`)
- User avatars (`[data-testid="user-avatar"]`)
- Agent status indicators (color changes)
- Progress bars (animated values)

### Task 5: Run Full Test Suite (30 minutes)
**Objective**: Execute all tests and capture baseline screenshots

**Expected Results**:
- All 9 pages load successfully
- Screenshots captured without errors
- Zero false positives (all dynamic content masked)

---

## Technical Requirements (from PLAN-v8-FINAL)

### Playwright Configuration (Research-Backed)
```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    viewport: { width: 1280, height: 720 },  // Fixed resolution
    deviceScaleFactor: 1,
    isMobile: false,
    hasTouch: false,
    locale: 'en-US',
    timezoneId: 'America/New_York',

    // Headless mode (consistent rendering)
    headless: true,

    // Browser context options
    browserName: 'chromium',
    channel: 'chrome',  // Stable Chrome channel

    // CRITICAL: Extended timeout for complex pages
    actionTimeout: 30000,  // 30s (not default 5s)
    navigationTimeout: 30000,  // 30s
  },

  // Animation disabling (prevent mid-animation captures)
  styleTagOptions: {
    content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
      }
    `
  }
});
```

### Screenshot Capture with Retry (Research-Backed)
```typescript
// Helper function for screenshot capture with exponential backoff
export async function captureWithRetry(
  page: Page,
  url: string,
  screenshotName: string,
  maxRetries: number = 3
): Promise<Buffer> {
  const delays = [5000, 10000, 30000]; // Exponential backoff

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      await page.goto(url, { timeout: delays[attempt] });

      // CRITICAL: Wait for WebGL initialization (if 3D implemented)
      if (url.includes('loop2') || url.includes('loop1')) {
        await page.waitForFunction(() => {
          const canvas = document.querySelector('canvas');
          return canvas && canvas.getContext('webgl') !== null;
        }, { timeout: delays[attempt] });
      }

      // Wait for stable state
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(500); // Buffer for animations

      // CRITICAL: Mask dynamic content
      await expect(page).toHaveScreenshot(screenshotName, {
        maxDiffPixelRatio: 0.01,  // 1% tolerance
        threshold: 0.2,            // Color similarity
        animations: 'disabled',
        mask: [
          page.locator('[data-testid="timestamp"]'),
          page.locator('[data-testid="user-avatar"]'),
          page.locator('.dynamic-content')
        ]
      });

      return await page.screenshot({ fullPage: true });
    } catch (error) {
      if (attempt === maxRetries - 1) {
        // CRITICAL: Manual approval fallback
        console.error(`Screenshot failed for ${url}. Manual approval required.`);
        throw error;
      }
      console.log(`Retry ${attempt + 1}/${maxRetries} for ${url}`);
    }
  }

  throw new Error('Max retries exceeded');
}
```

---

## Expected Outcomes

### Day 1 Deliverables
1. **Playwright Configuration** (updated with 30s timeout)
2. **Chromium Browser** (installed and functional)
3. **E2E Test Suite** (all 9 pages covered)
4. **Screenshot Baseline** (visual regression baseline captured)
5. **Test Results** (all tests passing, <10% false positives)

### Quality Metrics
| Metric | Target | Status |
|--------|--------|--------|
| **Pages Tested** | 9/9 (100%) | ⏳ Pending |
| **Screenshots Captured** | 9 baseline images | ⏳ Pending |
| **False Positive Rate** | <10% | ⏳ Pending |
| **Test Execution Time** | <5 minutes total | ⏳ Pending |
| **Timeout Handling** | 30s configured | ⏳ Pending |

---

## Next Steps (Day 2)

After Day 1 completion:
1. Manual browser testing of 3D visualizers
2. Cross-browser compatibility testing (Chrome, Firefox, Safari)
3. Mobile device testing (responsive design verification)
4. Accessibility audit (keyboard navigation, screen readers)

---

**Generated**: 2025-10-09T15:05:00-04:00
**Model**: Claude Sonnet 4.5
**Role**: Week 15 Implementation Specialist
**Status**: Day 1 IN PROGRESS
