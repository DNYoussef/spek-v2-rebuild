/**
 * Screenshot Capture Helper with Exponential Backoff Retry
 * Week 15 Day 1 - Research-Backed Implementation
 * Week 19 Update - Fixed for 3D pages that never reach networkidle
 *
 * Based on PLAN-v8-FINAL Week 15 specifications:
 * - 60s timeout + exponential backoff (10s, 30s, 60s)
 * - Dynamic content masking (timestamps, avatars, ads)
 * - WebGL initialization waiting (for 3D pages)
 * - Manual approval fallback (<10% rate target)
 *
 * Week 19 Fix: 3D pages (Loop 1/2/3) never reach networkidle due to
 * continuous Three.js animations. Changed to use 'load' + explicit waits.
 *
 * Target: <10% false positive rate
 */

import { Page, expect } from '@playwright/test';

export interface ScreenshotOptions {
  /**
   * URL to navigate to and capture
   */
  url: string;

  /**
   * Name for the screenshot file (e.g., 'homepage.png')
   */
  screenshotName: string;

  /**
   * Maximum number of retry attempts
   * @default 3
   */
  maxRetries?: number;

  /**
   * Whether this page contains 3D/WebGL content
   * @default false
   */
  has3DContent?: boolean;

  /**
   * Additional selectors to mask (dynamic content)
   * @default []
   */
  maskSelectors?: string[];

  /**
   * Wait for specific element before capturing
   * @default null
   */
  waitForSelector?: string;
}

/**
 * Capture screenshot with exponential backoff retry logic
 *
 * @param page - Playwright page object
 * @param options - Screenshot capture options
 * @returns Screenshot buffer
 * @throws Error if max retries exceeded
 */
export async function captureWithRetry(
  page: Page,
  options: ScreenshotOptions
): Promise<Buffer> {
  const {
    url,
    screenshotName,
    maxRetries = 3,
    has3DContent = false,
    maskSelectors = [],
    waitForSelector = null,
  } = options;

  // Exponential backoff delays (research-backed, Week 19: increased for 3D)
  const delays = [10000, 30000, 60000]; // 10s, 30s, 60s

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      console.log(`[Attempt ${attempt + 1}/${maxRetries}] Navigating to ${url}`);

      // Navigate with exponentially increasing timeout
      // Week 19: Use 'load' instead of 'networkidle' for 3D pages
      await page.goto(url, {
        timeout: delays[attempt],
        waitUntil: has3DContent ? 'load' : 'networkidle',
      });

      console.log(`[Attempt ${attempt + 1}/${maxRetries}] Navigation complete`);

      // CRITICAL: Wait for WebGL initialization (if 3D content)
      if (has3DContent) {
        console.log(`[Attempt ${attempt + 1}/${maxRetries}] Waiting for WebGL initialization...`);

        await page.waitForFunction(
          () => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return false;

            // Check if WebGL context exists
            const gl = canvas.getContext('webgl') || canvas.getContext('webgl2');
            return gl !== null;
          },
          {
            timeout: delays[attempt],
          }
        );

        console.log(`[Attempt ${attempt + 1}/${maxRetries}] WebGL initialized`);

        // Week 19: Additional settling time for 3D scene
        await page.waitForTimeout(3000); // 3s for Three.js to render
      }

      // Wait for specific element if provided
      if (waitForSelector) {
        console.log(
          `[Attempt ${attempt + 1}/${maxRetries}] Waiting for selector: ${waitForSelector}`
        );

        await page.waitForSelector(waitForSelector, {
          timeout: delays[attempt],
          state: 'visible',
        });
      }

      // Wait for page to be fully loaded and stable (skip for 3D pages)
      if (!has3DContent) {
        await page.waitForLoadState('networkidle');
      }

      // Buffer time for animations to settle
      await page.waitForTimeout(has3DContent ? 2000 : 500);

      console.log(`[Attempt ${attempt + 1}/${maxRetries}] Capturing screenshot...`);

      // Build mask locators (dynamic content exclusion)
      const defaultMasks = [
        '[data-testid="timestamp"]',
        '[data-testid="user-avatar"]',
        '.dynamic-content',
        '[data-dynamic="true"]',
      ];

      const allMasks = [...defaultMasks, ...maskSelectors];
      const maskLocators = allMasks
        .map((selector) => page.locator(selector))
        .filter(Boolean);

      // CRITICAL: Capture screenshot with masking
      await expect(page).toHaveScreenshot(screenshotName, {
        maxDiffPixelRatio: 0.01, // 1% tolerance (research-validated)
        threshold: 0.2, // 20% color similarity
        animations: 'disabled', // Prevent mid-animation captures
        mask: maskLocators, // Mask dynamic content
        fullPage: true, // Capture entire page
      });

      console.log(`[Attempt ${attempt + 1}/${maxRetries}] Screenshot captured successfully`);

      // Return full page screenshot buffer
      return await page.screenshot({ fullPage: true });
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);

      console.error(
        `[Attempt ${attempt + 1}/${maxRetries}] Screenshot failed: ${errorMessage}`
      );

      // If this was the last retry, throw error
      if (attempt === maxRetries - 1) {
        console.error(
          `❌ MANUAL APPROVAL REQUIRED: Screenshot failed for ${url} after ${maxRetries} attempts`
        );
        console.error(`   Error: ${errorMessage}`);
        console.error(`   Please review manually and update visual baseline if needed.`);

        throw new Error(
          `Screenshot capture failed after ${maxRetries} retries for ${url}: ${errorMessage}`
        );
      }

      // Log retry
      console.log(
        `[Retry ${attempt + 1}/${maxRetries}] Retrying in ${delays[attempt + 1]}ms...`
      );
    }
  }

  throw new Error(`Max retries (${maxRetries}) exceeded for ${url}`);
}

/**
 * Wait for 3D scene to be fully rendered
 *
 * @param page - Playwright page object
 * @param timeout - Maximum wait time in ms
 */
export async function waitFor3DScene(page: Page, timeout: number = 10000): Promise<void> {
  await page.waitForFunction(
    () => {
      const canvas = document.querySelector('canvas');
      if (!canvas) return false;

      // Check if WebGL context is available
      const gl = canvas.getContext('webgl') || canvas.getContext('webgl2');
      if (!gl) return false;

      // Check if scene has been rendered (canvas not blank)
      const pixels = new Uint8Array(4);
      gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, pixels);

      // If any pixel value is non-zero, scene has rendered
      return pixels.some((val) => val > 0);
    },
    { timeout }
  );
}

/**
 * Mask all timestamps on the page
 *
 * @param page - Playwright page object
 */
export async function maskTimestamps(page: Page): Promise<void> {
  await page.addStyleTag({
    content: `
      [data-testid="timestamp"],
      time,
      .timestamp,
      [datetime] {
        opacity: 0 !important;
        visibility: hidden !important;
      }
    `,
  });
}

/**
 * Mask all user avatars on the page
 *
 * @param page - Playwright page object
 */
export async function maskAvatars(page: Page): Promise<void> {
  await page.addStyleTag({
    content: `
      [data-testid="user-avatar"],
      .avatar,
      img[alt*="avatar" i],
      img[alt*="profile" i] {
        opacity: 0 !important;
        visibility: hidden !important;
      }
    `,
  });
}

/**
 * Disable all animations on the page
 *
 * @param page - Playwright page object
 */
export async function disableAnimations(page: Page): Promise<void> {
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
        transition: none !important;
      }
    `,
  });
}
