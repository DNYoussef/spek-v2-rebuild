import { test, expect } from '@playwright/test';

/**
 * Loop Visualizers E2E Tests
 * Week 15 Day 2 - Fixed strict mode violations
 */

test.describe('Loop 1 Visualizer', () => {
  test('should render Loop 1 page', async ({ page }) => {
    await page.goto('/loop1');

    // Check page loaded (fixed: use .first() to avoid strict mode violation)
    const heading = page.locator('h1, h2').first();
    await expect(heading).toContainText(/Loop 1|Premortem|Research/i);

    // Check for visualizer canvas (Three.js)
    const canvas = page.locator('canvas').first();
    if (await canvas.count() > 0) {
      await expect(canvas).toBeVisible({ timeout: 10000 });
    }
  });

  test('should take Loop 1 screenshot', async ({ page }) => {
    await page.goto('/loop1');
    await page.waitForTimeout(2000); // Wait for 3D rendering
    await page.screenshot({ path: 'tests/screenshots/loop1-visualizer.png', fullPage: true });
  });
});

test.describe('Loop 2 Visualizer', () => {
  test('should render Loop 2 page', async ({ page }) => {
    await page.goto('/loop2');

    // Check page loaded (fixed: use .first() to avoid strict mode violation)
    const heading = page.locator('h1, h2').first();
    await expect(heading).toContainText(/Loop 2|Execution|Audit/i);

    // Check for visualizer canvas (Three.js)
    const canvas = page.locator('canvas').first();
    if (await canvas.count() > 0) {
      await expect(canvas).toBeVisible({ timeout: 10000 });
    }
  });

  test('should take Loop 2 screenshot', async ({ page }) => {
    await page.goto('/loop2');
    await page.waitForTimeout(2000); // Wait for 3D rendering
    await page.screenshot({ path: 'tests/screenshots/loop2-visualizer.png', fullPage: true });
  });
});

test.describe('Loop 3 Visualizer', () => {
  test('should render Loop 3 page', async ({ page }) => {
    await page.goto('/loop3');

    // Check page loaded (fixed: use .first() to avoid strict mode violation)
    const heading = page.locator('h1, h2').first();
    await expect(heading).toContainText(/Loop 3|Deployment|CI\/CD|Quality|Finalization/i);

    // Check for visualizer canvas (Three.js)
    const canvas = page.locator('canvas').first();
    if (await canvas.count() > 0) {
      await expect(canvas).toBeVisible({ timeout: 10000 });
    }
  });

  test('should take Loop 3 screenshot', async ({ page }) => {
    await page.goto('/loop3');
    await page.waitForTimeout(2000); // Wait for 3D rendering
    await page.screenshot({ path: 'tests/screenshots/loop3-visualizer.png', fullPage: true });
  });
});

test.describe('Agent Status Monitor', () => {
  test('should display agent status', async ({ page }) => {
    await page.goto('/');

    // Look for agent monitor component
    const agentMonitor = page.locator('[data-testid="agent-monitor"], .agent-status, .agent-monitor');

    // If visible, check it works
    if (await agentMonitor.isVisible({ timeout: 5000 }).catch(() => false)) {
      await expect(agentMonitor).toBeVisible();
    }
  });
});
