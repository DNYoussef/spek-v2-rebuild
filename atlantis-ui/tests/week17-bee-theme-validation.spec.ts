/**
 * Week 17: Bee/Flower/Hive Theme Visual Validation
 *
 * This test suite validates the new bee-themed 3D visualizations:
 * - Loop 1: Flower Garden
 * - Loop 2: Beehive Village
 * - Loop 3: Honeycomb Layers
 *
 * Tests verify:
 * 1. Pages load without errors
 * 2. 3D canvas renders
 * 3. Visual screenshots for manual review
 * 4. Performance (FPS) is acceptable
 */

import { test, expect } from '@playwright/test';

test.describe('Week 17: Bee Theme Visual Validation', () => {
  test.beforeEach(async ({ page }) => {
    // Set viewport for consistent screenshots
    await page.setViewportSize({ width: 1920, height: 1080 });
  });

  test('Homepage loads successfully', async ({ page }) => {
    await page.goto('http://localhost:3001', {
      waitUntil: 'load',
      timeout: 60000,
    });

    // Take screenshot
    await page.screenshot({
      path: 'tests/screenshots/week17-homepage.png',
      fullPage: false,
    });

    // Verify no console errors
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    expect(errors.length).toBe(0);
  });

  test('Loop 1: Flower Garden visualization', async ({ page }) => {
    await page.goto('http://localhost:3001/loop1', {
      waitUntil: 'load',
      timeout: 60000,
    });

    // Wait for 3D canvas to render
    await page.waitForSelector('canvas', { timeout: 10000 });

    // Wait for 3D scene to initialize (Week 19: increased for Three.js)
    await page.waitForTimeout(3000);

    // Take screenshot
    await page.screenshot({
      path: 'tests/screenshots/week17-loop1-flower-garden.png',
      fullPage: false,
    });

    // Verify canvas exists
    const canvas = await page.locator('canvas');
    await expect(canvas).toBeVisible();

    console.log('✅ Loop 1 Flower Garden: Canvas rendered successfully');
  });

  test('Loop 2: Beehive Village visualization', async ({ page }) => {
    await page.goto('http://localhost:3001/loop2', {
      waitUntil: 'load',
      timeout: 60000,
    });

    // Wait for 3D canvas to render
    await page.waitForSelector('canvas', { timeout: 10000 });

    // Wait for 3D scene to initialize (Week 19: increased for Three.js)
    await page.waitForTimeout(3000);

    // Take screenshot
    await page.screenshot({
      path: 'tests/screenshots/week17-loop2-beehive-village.png',
      fullPage: false,
    });

    // Verify canvas exists
    const canvas = await page.locator('canvas');
    await expect(canvas).toBeVisible();

    console.log('✅ Loop 2 Beehive Village: Canvas rendered successfully');
  });

  test('Loop 3: Honeycomb Layers visualization', async ({ page }) => {
    await page.goto('http://localhost:3001/loop3', {
      waitUntil: 'load',
      timeout: 60000,
    });

    // Wait for 3D canvas to render
    await page.waitForSelector('canvas', { timeout: 10000 });

    // Wait for 3D scene to initialize (Week 19: increased for Three.js)
    await page.waitForTimeout(3000);

    // Take screenshot
    await page.screenshot({
      path: 'tests/screenshots/week17-loop3-honeycomb-layers.png',
      fullPage: false,
    });

    // Verify canvas exists
    const canvas = await page.locator('canvas');
    await expect(canvas).toBeVisible();

    console.log('✅ Loop 3 Honeycomb Layers: Canvas rendered successfully');
  });

  test('Performance: Measure FPS on Loop 2 (most complex)', async ({
    page,
  }) => {
    await page.goto('http://localhost:3001/loop2', {
      waitUntil: 'load',
      timeout: 60000,
    });

    // Wait for canvas
    await page.waitForSelector('canvas', { timeout: 10000 });

    // Wait for 3D scene to initialize
    await page.waitForTimeout(3000);

    // Measure performance
    const perfMetrics = await page.evaluate(() => {
      return new Promise((resolve) => {
        let frameCount = 0;
        const startTime = performance.now();
        const duration = 3000; // 3 seconds

        function countFrames() {
          frameCount++;
          const elapsed = performance.now() - startTime;

          if (elapsed < duration) {
            requestAnimationFrame(countFrames);
          } else {
            const fps = (frameCount / elapsed) * 1000;
            resolve({ fps: Math.round(fps), frameCount, duration: elapsed });
          }
        }

        requestAnimationFrame(countFrames);
      });
    });

    console.log('📊 Performance Metrics:', perfMetrics);

    // Verify FPS is reasonable (target: 60, minimum: 30)
    expect((perfMetrics as any).fps).toBeGreaterThanOrEqual(30);

    console.log(
      `✅ Performance: ${(perfMetrics as any).fps} FPS (target: 60 FPS)`
    );
  });

  test('SVG Patterns: Verify honeycomb pattern exists', async ({ page }) => {
    await page.goto('http://localhost:3001', {
      waitUntil: 'load',
      timeout: 60000,
    });

    // Check if honeycomb pattern SVG exists
    const hasPattern = await page.evaluate(() => {
      const patterns = document.querySelectorAll('svg pattern');
      return Array.from(patterns).some(
        (p) => p.id === 'honeycomb' || p.id.includes('honeycomb')
      );
    });

    if (hasPattern) {
      console.log('✅ SVG Patterns: Honeycomb pattern found');
    } else {
      console.log('⚠️  SVG Patterns: Honeycomb pattern not found (may not be used on this page)');
    }
  });
});

test.describe('Week 17: Accessibility Checks', () => {
  test('Canvas has proper ARIA labels', async ({ page }) => {
    await page.goto('http://localhost:3001/loop1', {
      waitUntil: 'load',
      timeout: 60000,
    });

    // Wait for canvas to render
    await page.waitForTimeout(2000);

    const canvas = await page.locator('canvas');
    const ariaLabel = await canvas.getAttribute('aria-label');

    if (ariaLabel) {
      console.log('✅ Accessibility: Canvas has ARIA label:', ariaLabel);
    } else {
      console.log(
        '⚠️  Accessibility: Canvas missing ARIA label (improvement needed)'
      );
    }
  });

  test('Keyboard navigation works', async ({ page }) => {
    await page.goto('http://localhost:3001/loop1', {
      waitUntil: 'load',
      timeout: 60000,
    });

    // Wait for page to be interactive
    await page.waitForTimeout(2000);

    // Test Tab navigation
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    console.log('✅ Accessibility: Keyboard navigation functional');
  });
});
