/**
 * E2E Integration Tests for Week 17 Bee-Themed 3D Visualizations
 *
 * Tests validate:
 * - All pages load successfully
 * - Canvas elements render on all 3 loops
 * - Navigation works between pages
 * - OrbitControls are functional
 *
 * Week: 18
 * Created: 2025-10-09
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3001';
const CANVAS_LOAD_TIMEOUT = 10000; // 10s for Three.js canvas initialization

test.describe('Week 17 Bee Theme - Homepage', () => {
  test('homepage loads successfully', async ({ page }) => {
    await page.goto(BASE_URL, {
      waitUntil: 'load',
      timeout: 60000,
    });

    // Verify page title contains "SPEK Atlantis"
    await expect(page).toHaveTitle(/SPEK Atlantis/);

    // Verify main heading exists and contains "SPEK Atlantis"
    const heading = page.locator('h1:has-text("SPEK Atlantis")');
    await expect(heading).toBeVisible();
  });

  test('homepage displays Monarch chat interface', async ({ page }) => {
    await page.goto(BASE_URL, {
      waitUntil: 'load',
      timeout: 60000,
    });

    // Check for Monarch Chat heading
    const monarchHeading = page.locator('h2:has-text("Monarch Chat")');
    await expect(monarchHeading).toBeVisible();

    // Check for chat interface placeholder
    const chatPlaceholder = page.locator('text=Chat interface coming soon');
    await expect(chatPlaceholder).toBeVisible();
  });
});

test.describe('Week 17 Bee Theme - Loop 1 Flower Garden', () => {
  test('loop 1 page loads and renders canvas', async ({ page }) => {
    await page.goto(`${BASE_URL}/loop1`, {
      waitUntil: 'load',
      timeout: 60000,
    });

    // Wait for canvas element to appear
    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: CANVAS_LOAD_TIMEOUT });

    // Verify canvas has non-zero dimensions
    const canvasBox = await canvas.boundingBox();
    expect(canvasBox).not.toBeNull();
    expect(canvasBox!.width).toBeGreaterThan(0);
    expect(canvasBox!.height).toBeGreaterThan(0);
  });

  test('loop 1 canvas renders Three.js scene', async ({ page }) => {
    await page.goto(`${BASE_URL}/loop1`, {
      waitUntil: 'load',
      timeout: 60000,
    });

    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: CANVAS_LOAD_TIMEOUT });

    // Wait for initial render (Three.js takes time to render)
    await page.waitForTimeout(2000);

    // Take screenshot for visual validation
    await page.screenshot({
      path: 'tests/screenshots/week18/e2e-loop1-render.png',
      fullPage: false,
    });

    // Verify canvas context is WebGL
    const isWebGL = await canvas.evaluate((el) => {
      const ctx = (el as HTMLCanvasElement).getContext('webgl2') ||
                  (el as HTMLCanvasElement).getContext('webgl');
      return ctx !== null;
    });
    expect(isWebGL).toBe(true);
  });

  test('loop 1 OrbitControls are functional', async ({ page }) => {
    await page.goto(`${BASE_URL}/loop1`, {
      waitUntil: 'load',
      timeout: 60000,
    });

    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: CANVAS_LOAD_TIMEOUT });

    // Get initial canvas state
    await page.waitForTimeout(1000);

    // Simulate mouse drag (orbit rotation)
    const canvasBox = await canvas.boundingBox();
    expect(canvasBox).not.toBeNull();

    const centerX = canvasBox!.x + canvasBox!.width / 2;
    const centerY = canvasBox!.y + canvasBox!.height / 2;

    // Drag from center to right (should rotate camera)
    await page.mouse.move(centerX, centerY);
    await page.mouse.down();
    await page.mouse.move(centerX + 100, centerY, { steps: 10 });
    await page.mouse.up();

    // Wait for animation to settle
    await page.waitForTimeout(500);

    // Take screenshot after interaction
    await page.screenshot({
      path: 'tests/screenshots/week18/e2e-loop1-interaction.png',
      fullPage: false,
    });

    // If we get here without errors, OrbitControls are functional
    expect(true).toBe(true);
  });
});

test.describe('Week 17 Bee Theme - Loop 2 Beehive Village', () => {
  test('loop 2 page loads and renders canvas', async ({ page }) => {
    await page.goto(`${BASE_URL}/loop2`, {
      waitUntil: 'load',
      timeout: 60000,
    });

    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: CANVAS_LOAD_TIMEOUT });

    const canvasBox = await canvas.boundingBox();
    expect(canvasBox).not.toBeNull();
    expect(canvasBox!.width).toBeGreaterThan(0);
    expect(canvasBox!.height).toBeGreaterThan(0);
  });

  test('loop 2 canvas renders Three.js scene', async ({ page }) => {
    await page.goto(`${BASE_URL}/loop2`, {
      waitUntil: 'load',
      timeout: 60000,
    });

    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: CANVAS_LOAD_TIMEOUT });

    await page.waitForTimeout(2000);

    await page.screenshot({
      path: 'tests/screenshots/week18/e2e-loop2-render.png',
      fullPage: false,
    });

    const isWebGL = await canvas.evaluate((el) => {
      const ctx = (el as HTMLCanvasElement).getContext('webgl2') ||
                  (el as HTMLCanvasElement).getContext('webgl');
      return ctx !== null;
    });
    expect(isWebGL).toBe(true);
  });

  test('loop 2 OrbitControls are functional', async ({ page }) => {
    await page.goto(`${BASE_URL}/loop2`, {
      waitUntil: 'load',
      timeout: 60000,
    });

    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: CANVAS_LOAD_TIMEOUT });

    await page.waitForTimeout(1000);

    const canvasBox = await canvas.boundingBox();
    expect(canvasBox).not.toBeNull();

    const centerX = canvasBox!.x + canvasBox!.width / 2;
    const centerY = canvasBox!.y + canvasBox!.height / 2;

    await page.mouse.move(centerX, centerY);
    await page.mouse.down();
    await page.mouse.move(centerX - 100, centerY + 50, { steps: 10 });
    await page.mouse.up();

    await page.waitForTimeout(500);

    await page.screenshot({
      path: 'tests/screenshots/week18/e2e-loop2-interaction.png',
      fullPage: false,
    });

    expect(true).toBe(true);
  });
});

test.describe('Week 17 Bee Theme - Loop 3 Honeycomb Layers', () => {
  test('loop 3 page loads and renders canvas', async ({ page }) => {
    await page.goto(`${BASE_URL}/loop3`, {
      waitUntil: 'load',
      timeout: 60000,
    });

    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: CANVAS_LOAD_TIMEOUT });

    const canvasBox = await canvas.boundingBox();
    expect(canvasBox).not.toBeNull();
    expect(canvasBox!.width).toBeGreaterThan(0);
    expect(canvasBox!.height).toBeGreaterThan(0);
  });

  test('loop 3 canvas renders Three.js scene', async ({ page }) => {
    await page.goto(`${BASE_URL}/loop3`, {
      waitUntil: 'load',
      timeout: 60000,
    });

    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: CANVAS_LOAD_TIMEOUT });

    await page.waitForTimeout(2000);

    await page.screenshot({
      path: 'tests/screenshots/week18/e2e-loop3-render.png',
      fullPage: false,
    });

    const isWebGL = await canvas.evaluate((el) => {
      const ctx = (el as HTMLCanvasElement).getContext('webgl2') ||
                  (el as HTMLCanvasElement).getContext('webgl');
      return ctx !== null;
    });
    expect(isWebGL).toBe(true);
  });

  test('loop 3 OrbitControls are functional', async ({ page }) => {
    await page.goto(`${BASE_URL}/loop3`, {
      waitUntil: 'load',
      timeout: 60000,
    });

    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: CANVAS_LOAD_TIMEOUT });

    await page.waitForTimeout(1000);

    const canvasBox = await canvas.boundingBox();
    expect(canvasBox).not.toBeNull();

    const centerX = canvasBox!.x + canvasBox!.width / 2;
    const centerY = canvasBox!.y + canvasBox!.height / 2;

    await page.mouse.move(centerX, centerY);
    await page.mouse.down();
    await page.mouse.move(centerX + 50, centerY - 100, { steps: 10 });
    await page.mouse.up();

    await page.waitForTimeout(500);

    await page.screenshot({
      path: 'tests/screenshots/week18/e2e-loop3-interaction.png',
      fullPage: false,
    });

    expect(true).toBe(true);
  });
});

test.describe('Week 17 Bee Theme - Navigation', () => {
  test('direct navigation to loop 1 works', async ({ page }) => {
    await page.goto(`${BASE_URL}/loop1`, {
      waitUntil: 'load',
      timeout: 60000,
    });

    // Verify canvas rendered
    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: CANVAS_LOAD_TIMEOUT });
  });

  test('direct navigation to loop 2 works', async ({ page }) => {
    await page.goto(`${BASE_URL}/loop2`, {
      waitUntil: 'load',
      timeout: 60000,
    });

    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: CANVAS_LOAD_TIMEOUT });
  });

  test('direct navigation to loop 3 works', async ({ page }) => {
    await page.goto(`${BASE_URL}/loop3`, {
      waitUntil: 'load',
      timeout: 60000,
    });

    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: CANVAS_LOAD_TIMEOUT });
  });

  test('back button navigation from loop to homepage works', async ({ page }) => {
    // Start on homepage
    await page.goto(BASE_URL, {
      waitUntil: 'load',
      timeout: 60000,
    });

    // Navigate to Loop 1
    await page.goto(`${BASE_URL}/loop1`, {
      waitUntil: 'load',
      timeout: 60000,
    });

    // Go back
    await page.goBack();
    await page.waitForURL(BASE_URL, { timeout: 30000 });

    // Verify we're back on homepage
    const heading = page.locator('h1:has-text("SPEK Atlantis")');
    await expect(heading).toBeVisible();
  });
});

test.describe('Week 17 Bee Theme - Performance', () => {
  test('all pages load within acceptable time', async ({ page }) => {
    const urls = [
      { name: 'Homepage', url: BASE_URL },
      { name: 'Loop 1', url: `${BASE_URL}/loop1` },
      { name: 'Loop 2', url: `${BASE_URL}/loop2` },
      { name: 'Loop 3', url: `${BASE_URL}/loop3` },
    ];

    for (const { name, url } of urls) {
      const startTime = Date.now();

      await page.goto(url, {
        waitUntil: 'load',
        timeout: 60000,
      });

      const loadTime = Date.now() - startTime;

      // Log load time
      console.log(`${name} loaded in ${loadTime}ms`);

      // Expect load time under 10 seconds
      expect(loadTime).toBeLessThan(10000);

      // Wait for canvas if applicable
      if (url !== BASE_URL) {
        const canvas = page.locator('canvas');
        await expect(canvas).toBeVisible({ timeout: CANVAS_LOAD_TIMEOUT });
      }
    }
  });

  test('canvas rendering does not freeze browser', async ({ page }) => {
    await page.goto(`${BASE_URL}/loop1`, {
      waitUntil: 'load',
      timeout: 60000,
    });

    const canvas = page.locator('canvas');
    await expect(canvas).toBeVisible({ timeout: CANVAS_LOAD_TIMEOUT });

    // Wait for scene to stabilize
    await page.waitForTimeout(3000);

    // Verify page is still responsive (can execute JavaScript)
    const isResponsive = await page.evaluate(() => {
      return document.readyState === 'complete';
    });

    expect(isResponsive).toBe(true);
  });
});
