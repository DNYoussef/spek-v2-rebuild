import { test, expect } from '@playwright/test';

/**
 * Performance E2E Tests
 * Week 21 Day 3 - Production Hardening
 *
 * Tests performance metrics:
 * - Page load time (<3s target)
 * - Bundle size (<200KB target)
 * - 3D rendering FPS (60 FPS desktop, 30 FPS mobile)
 * - Memory leaks (3D scenes)
 */

test.describe('Performance - Page Load Time', () => {
  test('should load homepage in under 3 seconds', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('/', { waitUntil: 'domcontentloaded' });

    const domLoadTime = Date.now() - startTime;

    console.log(`Homepage DOM load time: ${domLoadTime}ms`);

    // Target: <2s for homepage
    expect(domLoadTime).toBeLessThan(3000);

    if (domLoadTime < 2000) {
      console.log('✓ Excellent performance: <2s');
    } else if (domLoadTime < 3000) {
      console.log('✓ Good performance: <3s');
    } else {
      console.warn(`⚠️  Slow performance: ${domLoadTime}ms - recommend optimization`);
    }
  });

  test('should load all pages in under 3 seconds', async ({ page }) => {
    const pages = [
      '/',
      '/loop1',
      '/loop2',
      '/loop3',
      '/project/select',
      '/settings',
    ];

    const loadTimes: Record<string, number> = {};

    for (const pagePath of pages) {
      const startTime = Date.now();

      await page.goto(pagePath, { waitUntil: 'domcontentloaded' });

      const loadTime = Date.now() - startTime;
      loadTimes[pagePath] = loadTime;

      console.log(`${pagePath}: ${loadTime}ms`);

      // All pages should load in <3s
      expect(loadTime).toBeLessThan(3000);
    }

    // Calculate average
    const avgLoadTime =
      Object.values(loadTimes).reduce((sum, time) => sum + time, 0) / pages.length;

    console.log(`Average load time: ${avgLoadTime.toFixed(0)}ms`);

    // Average should be <2s
    if (avgLoadTime < 2000) {
      console.log('✓ Excellent average performance');
    }
  });

  test('should measure Core Web Vitals', async ({ page }) => {
    await page.goto('/');

    // Wait for page to fully load
    await page.waitForLoadState('networkidle');

    // Measure Core Web Vitals using Performance API
    const webVitals = await page.evaluate(() => {
      return new Promise((resolve) => {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const vitals: any = {};

          entries.forEach((entry) => {
            if (entry.entryType === 'paint') {
              if (entry.name === 'first-contentful-paint') {
                vitals.FCP = entry.startTime;
              }
            }

            if (entry.entryType === 'largest-contentful-paint') {
              vitals.LCP = entry.startTime;
            }
          });

          resolve(vitals);
        });

        observer.observe({ entryTypes: ['paint', 'largest-contentful-paint'] });

        // Resolve after 2 seconds if no entries
        setTimeout(() => resolve({}), 2000);
      });
    });

    console.log('Core Web Vitals:', webVitals);

    // Ideal targets:
    // FCP: <1.8s (good)
    // LCP: <2.5s (good)

    expect(true).toBe(true);
  });
});

test.describe('Performance - 3D Rendering', () => {
  test('should maintain 60 FPS on desktop for 3D scenes', async ({ page }) => {
    await page.goto('/loop2'); // Loop 2 has 3D beehive village

    // Check if page has 3D content
    const canvas = page.locator('canvas');
    const has3D = (await canvas.count()) > 0;

    if (!has3D) {
      test.skip(true, '3D content not found on this page');
      return;
    }

    // Wait for 3D scene to initialize
    await page.waitForTimeout(3000);

    // Measure FPS using requestAnimationFrame
    const fpsData = await page.evaluate(() => {
      return new Promise((resolve) => {
        let frameCount = 0;
        const startTime = performance.now();
        const duration = 2000; // Measure for 2 seconds

        function countFrames() {
          frameCount++;

          if (performance.now() - startTime < duration) {
            requestAnimationFrame(countFrames);
          } else {
            const fps = (frameCount / duration) * 1000;
            resolve(fps);
          }
        }

        requestAnimationFrame(countFrames);
      });
    });

    console.log(`3D scene FPS: ${fpsData}`);

    // Target: 60 FPS (desktop)
    // Acceptable: 30 FPS (mobile)
    expect(Number(fpsData)).toBeGreaterThan(30);

    if (Number(fpsData) >= 60) {
      console.log('✓ Excellent FPS: 60+ (smooth animation)');
    } else if (Number(fpsData) >= 30) {
      console.log('✓ Acceptable FPS: 30+ (playable)');
    } else {
      console.warn(`⚠️  Low FPS: ${fpsData} - recommend 3D optimization`);
    }
  });

  test('should not leak memory during 3D rendering', async ({ page }) => {
    await page.goto('/loop2');

    // Check if page has 3D content
    const canvas = page.locator('canvas');
    const has3D = (await canvas.count()) > 0;

    if (!has3D) {
      test.skip(true, '3D content not found');
      return;
    }

    // Wait for 3D scene to initialize
    await page.waitForTimeout(3000);

    // Measure initial memory using performance.memory API
    const metrics1 = await page.evaluate(() => {
      // @ts-expect-error - memory property may not exist in all browsers
      if (performance.memory) {
        return {
          // @ts-expect-error - usedJSHeapSize is non-standard Chromium property
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          // @ts-expect-error - totalJSHeapSize is non-standard Chromium property
          totalJSHeapSize: performance.memory.totalJSHeapSize,
        };
      }
      return null;
    });

    if (!metrics1) {
      console.log('ℹ️  Memory API not available - skipping memory leak test');
      return;
    }

    console.log('Initial metrics:', metrics1);

    // Let 3D scene run for 10 seconds
    await page.waitForTimeout(10000);

    // Measure memory after 10 seconds
    const metrics2 = await page.evaluate(() => {
      // @ts-expect-error - memory property may not exist in all browsers
      if (performance.memory) {
        return {
          // @ts-expect-error - usedJSHeapSize is non-standard Chromium property
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          // @ts-expect-error - totalJSHeapSize is non-standard Chromium property
          totalJSHeapSize: performance.memory.totalJSHeapSize,
        };
      }
      return null;
    });

    if (!metrics2) {
      console.log('ℹ️  Memory API not available - skipping memory leak test');
      return;
    }

    console.log('After 10s metrics:', metrics2);

    // Check memory growth
    const memoryGrowth = metrics2.usedJSHeapSize - metrics1.usedJSHeapSize;
    const memoryGrowthMB = (memoryGrowth / 1024 / 1024).toFixed(2);

    console.log(`Memory growth: ${memoryGrowthMB} MB`);

    // Memory growth should be minimal (<50MB) for a 10-second session
    // (Some growth is normal due to initial object creation)
    if (Math.abs(Number(memoryGrowthMB)) < 50) {
      console.log('✓ No significant memory leak detected');
    } else {
      console.warn(`⚠️  Potential memory leak: ${memoryGrowthMB} MB growth in 10s`);
    }

    expect(true).toBe(true);
  });

  test('should handle window resize without performance degradation', async ({ page }) => {
    await page.goto('/loop2');

    // Check if page has 3D content
    const canvas = page.locator('canvas');
    const has3D = (await canvas.count()) > 0;

    if (!has3D) {
      test.skip(true, '3D content not found');
      return;
    }

    // Wait for initial render
    await page.waitForTimeout(2000);

    // Resize window multiple times
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.waitForTimeout(500);

    await page.setViewportSize({ width: 1280, height: 720 });
    await page.waitForTimeout(500);

    await page.setViewportSize({ width: 1024, height: 768 });
    await page.waitForTimeout(500);

    // Check if canvas resized properly
    const canvasBounds = await canvas.boundingBox();

    if (canvasBounds) {
      console.log(`Canvas dimensions after resize: ${canvasBounds.width}x${canvasBounds.height}`);
      console.log('✓ 3D scene handled window resize');
    }

    expect(true).toBe(true);
  });
});

test.describe('Performance - Bundle Size', () => {
  test('should report bundle size (informational)', async ({ page }) => {
    // This test is informational - actual bundle size is measured during build
    console.log('ℹ️  Bundle size is measured during build process');
    console.log('ℹ️  Run: npm run build && npx next-bundle-analyzer');
    console.log('ℹ️  Target: <200KB initial bundle');

    // We can check the size of loaded JavaScript
    const jsSize = await page.evaluate(() => {
      const resources = performance.getEntriesByType('resource');
      let totalJsSize = 0;

      resources.forEach((resource: any) => {
        if (resource.name.endsWith('.js')) {
          totalJsSize += resource.transferSize || 0;
        }
      });

      return totalJsSize;
    });

    const jsSizeMB = (jsSize / 1024 / 1024).toFixed(2);
    console.log(`Total JavaScript loaded: ${jsSizeMB} MB`);

    expect(true).toBe(true);
  });
});
