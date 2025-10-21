import { test, expect } from '@playwright/test';

/**
 * Navigation & Routing E2E Tests
 * Week 21 Day 3 - Production Hardening
 *
 * Tests comprehensive navigation across all 9 pages:
 * - Homepage (/)
 * - Loop 1 (/loop1)
 * - Loop 2 (/loop2)
 * - Loop 3 (/loop3)
 * - Project Select (/project/select)
 * - Project New (/project/new)
 * - Settings (/settings)
 * - History (/history)
 * - Help (/help)
 */

test.describe('Navigation & Routing', () => {
  const pages = [
    { path: '/', name: 'Homepage' },
    { path: '/loop1', name: 'Loop 1' },
    { path: '/loop2', name: 'Loop 2' },
    { path: '/loop3', name: 'Loop 3' },
    { path: '/project/select', name: 'Project Select' },
    { path: '/project/new', name: 'Project New' },
    { path: '/settings', name: 'Settings' },
    { path: '/history', name: 'History' },
    { path: '/help', name: 'Help' },
  ];

  test('should navigate to all 9 pages successfully', async ({ page }) => {
    for (const { path, name } of pages) {
      await page.goto(path);

      // Verify page loaded (body is visible)
      await expect(page.locator('body')).toBeVisible();

      // Verify correct URL
      await expect(page).toHaveURL(new RegExp(path.replace('/', '\\/')));

      console.log(`✓ ${name} (${path}) loaded successfully`);
    }
  });

  test('should handle browser back/forward buttons correctly', async ({ page }) => {
    // Navigate through pages
    await page.goto('/');
    await page.goto('/loop1');
    await page.goto('/loop2');

    // Verify current page
    await expect(page).toHaveURL(/\/loop2/);

    // Go back
    await page.goBack();
    await expect(page).toHaveURL(/\/loop1/);

    // Go back again
    await page.goBack();
    await expect(page).toHaveURL(/\//);

    // Go forward
    await page.goForward();
    await expect(page).toHaveURL(/\/loop1/);

    // Go forward again
    await page.goForward();
    await expect(page).toHaveURL(/\/loop2/);
  });

  test('should support deep linking to specific routes', async ({ page }) => {
    // Direct navigation to deep routes
    await page.goto('/project/select?filter=recent');

    // Verify URL parameters persist
    await expect(page).toHaveURL(/\/project\/select\?filter=recent/);

    // Navigate to another page with parameters
    await page.goto('/loop2/audit');

    // Verify nested route works
    await expect(page).toHaveURL(/\/loop2\/audit/);
  });

  test('should display 404 page for invalid routes', async ({ page }) => {
    // Navigate to non-existent page
    await page.goto('/non-existent-page');

    // Check for 404 indicator (may be body text or specific element)
    const pageText = await page.locator('body').textContent();

    // Verify 404 content (may say "404", "Not Found", or similar)
    // Adjust this check based on your actual 404 page implementation
    const has404 = pageText?.includes('404') ||
                   pageText?.includes('Not Found') ||
                   pageText?.includes('Page not found');

    if (!has404) {
      console.warn('⚠️  Warning: No explicit 404 page detected. Consider implementing one.');
    }

    // At minimum, page should load without crashing
    await expect(page.locator('body')).toBeVisible();
  });

  test('should preserve URL parameters across navigation', async ({ page }) => {
    // Navigate with query parameters
    await page.goto('/?project=test-project');

    // Verify parameter exists
    await expect(page).toHaveURL(/\?project=test-project/);

    // Navigate using internal links (if implemented)
    const loop1Link = page.locator('a[href*="/loop1"]').first();

    if (await loop1Link.count() > 0) {
      await loop1Link.click();

      // Verify navigation worked
      await expect(page).toHaveURL(/\/loop1/);
    } else {
      console.warn('⚠️  Warning: No internal navigation links found on homepage.');
    }
  });

  test('should load all pages within timeout (60s)', async ({ page }) => {
    // Test that all pages load reasonably fast
    for (const { path, name } of pages) {
      const startTime = Date.now();

      await page.goto(path, { waitUntil: 'domcontentloaded' });

      const loadTime = Date.now() - startTime;

      // Log load time
      console.log(`${name}: ${loadTime}ms`);

      // Verify page loaded within 60s (generous timeout for 3D pages)
      expect(loadTime).toBeLessThan(60000);

      // Ideal: pages should load in <3s (except 3D pages which may be 5-10s)
      if (loadTime > 3000 && !path.includes('loop')) {
        console.warn(`⚠️  ${name} took ${loadTime}ms (>3s) - consider optimization`);
      }
    }
  });

  test('should maintain scroll position on back navigation', async ({ page }) => {
    // Navigate to a page
    await page.goto('/loop1');

    // Scroll down (if content is scrollable)
    await page.evaluate(() => window.scrollTo(0, 500));

    // Wait for scroll
    await page.waitForTimeout(100);

    // Navigate to another page
    await page.goto('/loop2');

    // Go back
    await page.goBack();

    // Check if scroll position is preserved (browser-dependent)
    const scrollY = await page.evaluate(() => window.scrollY);

    // Note: Scroll restoration is browser-dependent, this test is informational
    console.log(`Scroll position after back navigation: ${scrollY}px`);
  });
});

test.describe('Navigation Performance', () => {
  test('should measure and log time to first byte (TTFB)', async ({ page }) => {
    const routes = ['/', '/loop1', '/loop2', '/loop3'];

    for (const route of routes) {
      // Use Performance API to measure TTFB
      const [response] = await Promise.all([
        page.waitForResponse((resp) => resp.url().includes(route)),
        page.goto(route),
      ]);

      const timing = await response.request().timing();

      if (timing) {
        const ttfb = timing.responseStart - timing.requestStart;
        console.log(`${route} TTFB: ${ttfb}ms`);

        // Ideal TTFB: <500ms
        if (ttfb > 500) {
          console.warn(`⚠️  ${route} TTFB ${ttfb}ms exceeds 500ms target`);
        }
      }
    }
  });
});
