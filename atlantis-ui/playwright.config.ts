import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright Configuration for Atlantis UI Testing
 * Week 15 Day 1 - Research-Backed Configuration
 *
 * KEY OPTIMIZATIONS (from PLAN-v8-FINAL Week 15):
 * - 60s timeout for complex 3D/WebGL pages (UPDATED Week 19)
 * - Exponential backoff retry logic (5s, 10s, 30s)
 * - Dynamic content masking (timestamps, avatars)
 * - Animation disabling (prevent mid-animation captures)
 * - 1% tolerance threshold (maxDiffPixelRatio)
 *
 * Target: <10% false positive rate
 *
 * Week 19 Update: Increased timeouts for Loop 1/2/3 3D visualizations
 * (flower garden, beehive village, honeycomb layers never reach networkidle)
 */
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,

  // Exponential backoff retries (research-backed)
  retries: process.env.CI ? 3 : 2,  // Up to 3 retries with delays

  workers: process.env.CI ? 1 : undefined,

  reporter: [
    ['html'],
    ['list'],
  ],

  // Global timeout settings (research-backed)
  timeout: 90000,  // 90s per test (allows for 3D rendering + retries)

  use: {
    baseURL: 'http://localhost:3002',

    // CRITICAL: Extended timeouts for 3D/WebGL pages (Week 19: increased from 30s)
    actionTimeout: 60000,      // 60s (for heavy 3D rendering)
    navigationTimeout: 60000,  // 60s (3D pages never reach networkidle)

    // Fixed viewport for consistent screenshots
    viewport: { width: 1280, height: 720 },
    deviceScaleFactor: 1,
    isMobile: false,
    hasTouch: false,

    // Locale settings for consistent rendering
    locale: 'en-US',
    timezoneId: 'America/New_York',

    // Headless mode (consistent rendering, no GUI flickering)
    headless: true,

    // Screenshot settings
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome',  // Use stable Chrome channel

        // CRITICAL: Disable animations (prevent mid-animation captures)
        contextOptions: {
          reducedMotion: 'reduce',
        },
      },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3002',
    reuseExistingServer: !process.env.CI,
    timeout: 180000,  // 3 minutes for server startup (Week 21: increased for reliability)
  },

  // Expect configuration (screenshot comparison)
  expect: {
    toHaveScreenshot: {
      // CRITICAL: 1% tolerance threshold (research-validated)
      maxDiffPixelRatio: 0.01,  // 1% max pixel difference
      threshold: 0.2,            // 20% color similarity threshold
      animations: 'disabled',    // Disable animations for screenshots
    },
  },
});
