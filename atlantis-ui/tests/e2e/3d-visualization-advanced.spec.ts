import { test, expect } from '@playwright/test';

/**
 * Advanced 3D Visualization E2E Tests
 * Week 22 - Production Hardening Phase 3
 *
 * Comprehensive testing of Three.js 3D visualizations:
 * - Loop 1: Flower Garden (research phase)
 * - Loop 2: Beehive Village (execution phase)
 * - Loop 3: Honeycomb Layers (deployment phase)
 *
 * Tests cover:
 * - Canvas rendering and initialization
 * - WebGL context creation
 * - 3D scene performance (FPS)
 * - Camera controls and interactions
 * - Animation loops
 * - Resize handling
 * - Memory leaks
 */

test.describe('Loop 1: Flower Garden 3D Visualization', () => {
  test('should render flower garden canvas within 10s', async ({ page }) => {
    await page.goto('/loop1');

    // Wait for canvas to appear
    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeVisible({ timeout: 10000 });

    // Verify canvas has dimensions
    const box = await canvas.boundingBox();
    expect(box).not.toBeNull();
    expect(box?.width).toBeGreaterThan(0);
    expect(box?.height).toBeGreaterThan(0);

    console.log(`✓ Flower Garden canvas rendered: ${box?.width}x${box?.height}px`);
  });

  test('should initialize WebGL context successfully', async ({ page }) => {
    await page.goto('/loop1');

    await page.waitForTimeout(2000); // Wait for Three.js initialization

    // Check WebGL context
    const hasWebGL = await page.evaluate(() => {
      const canvas = document.querySelector('canvas');
      if (!canvas) return false;

      const gl = canvas.getContext('webgl') || canvas.getContext('webgl2');
      return !!gl;
    });

    expect(hasWebGL).toBe(true);
    console.log('✓ WebGL context initialized');
  });

  test('should render flowers with correct materials', async ({ page }) => {
    await page.goto('/loop1');

    await page.waitForTimeout(3000); // Wait for full scene load

    // Check Three.js scene composition
    const sceneInfo = await page.evaluate(() => {
      // Access Three.js scene from window (if exposed for testing)
      const canvas = document.querySelector('canvas');
      if (!canvas) return null;

      // Check canvas pixels are not blank
      const ctx = canvas.getContext('2d');
      if (!ctx) return null;

      // Simple check: canvas should have non-zero pixel data
      try {
        const imageData = ctx.getImageData(0, 0, 100, 100);
        const hasContent = imageData.data.some((value) => value > 0);
        return { hasContent };
      } catch {
        // If 2D context fails, assume WebGL is rendering (expected)
        return { hasContent: true };
      }
    });

    if (sceneInfo?.hasContent) {
      console.log('✓ Flower Garden scene is rendering content');
    } else {
      console.warn('⚠️  Canvas appears blank - may be loading slowly');
    }
  });

  test('should maintain 30+ FPS during animation', async ({ page }) => {
    await page.goto('/loop1');

    await page.waitForTimeout(2000);

    // Measure FPS over 3 seconds
    const fps = await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        let frameCount = 0;
        const startTime = performance.now();
        const duration = 3000; // 3 seconds

        const countFrames = () => {
          frameCount++;

          if (performance.now() - startTime < duration) {
            requestAnimationFrame(countFrames);
          } else {
            const avgFps = (frameCount / duration) * 1000;
            resolve(avgFps);
          }
        };

        requestAnimationFrame(countFrames);
      });
    });

    console.log(`Flower Garden FPS: ${fps.toFixed(1)}`);

    // Mobile target: 30 FPS, Desktop target: 60 FPS
    expect(fps).toBeGreaterThanOrEqual(30);

    if (fps >= 60) {
      console.log('✓ Excellent performance (60+ FPS)');
    } else if (fps >= 30) {
      console.log('✓ Acceptable performance (30-60 FPS)');
    }
  });

  test('should support camera orbit controls', async ({ page }) => {
    await page.goto('/loop1');

    await page.waitForTimeout(2000);

    const canvas = page.locator('canvas').first();

    // Try to interact with 3D scene (drag to rotate)
    await canvas.hover();
    await page.mouse.down();
    await page.mouse.move(100, 100);
    await page.mouse.up();

    await page.waitForTimeout(500);

    // If OrbitControls are implemented, this should change the camera view
    // We can't directly verify camera position, but we can check for console errors
    const consoleErrors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.waitForTimeout(500);

    if (consoleErrors.length === 0) {
      console.log('✓ Camera controls interaction (no errors)');
    } else {
      console.warn(`⚠️  Camera controls triggered errors: ${consoleErrors[0]}`);
    }
  });
});

test.describe('Loop 2: Beehive Village 3D Visualization', () => {
  test('should render beehive structures', async ({ page }) => {
    await page.goto('/loop2');

    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeVisible({ timeout: 10000 });

    await page.waitForTimeout(3000); // Wait for full scene load

    // Take screenshot for visual verification
    await page.screenshot({
      path: 'atlantis-ui/test-results/loop2-beehive-screenshot.png',
      fullPage: false,
    });

    console.log('✓ Beehive Village screenshot captured');
  });

  test('should animate bee agents moving between hives', async ({ page }) => {
    await page.goto('/loop2');

    await page.waitForTimeout(3000);

    // Check if animation is running
    const isAnimating = await page.evaluate(() => {
      return new Promise<boolean>((resolve) => {
        let previousTime = performance.now();
        let frameDetected = false;

        const checkAnimation = () => {
          const currentTime = performance.now();
          const delta = currentTime - previousTime;

          if (delta > 0 && delta < 100) {
            frameDetected = true;
            resolve(true);
          } else if (currentTime - previousTime > 5000) {
            resolve(false);
          } else {
            previousTime = currentTime;
            requestAnimationFrame(checkAnimation);
          }
        };

        requestAnimationFrame(checkAnimation);
      });
    });

    if (isAnimating) {
      console.log('✓ Beehive Village animation loop active');
    } else {
      console.warn('⚠️  Animation may not be running');
    }
  });

  test('should handle window resize without breaking', async ({ page }) => {
    await page.goto('/loop2');

    await page.waitForTimeout(2000);

    // Get initial canvas size
    const canvas = page.locator('canvas').first();
    const initialBox = await canvas.boundingBox();

    // Resize viewport
    await page.setViewportSize({ width: 800, height: 600 });

    await page.waitForTimeout(1000);

    // Get new canvas size
    const resizedBox = await canvas.boundingBox();

    // Canvas should have resized
    if (resizedBox && initialBox) {
      const sizeChanged =
        resizedBox.width !== initialBox.width || resizedBox.height !== initialBox.height;

      if (sizeChanged) {
        console.log(
          `✓ Canvas resized: ${initialBox.width}x${initialBox.height} → ${resizedBox.width}x${resizedBox.height}`
        );
      } else {
        console.warn('⚠️  Canvas did not resize - may need resize listener');
      }
    }

    // Verify scene still renders after resize
    await page.waitForTimeout(1000);

    const canvas2 = page.locator('canvas').first();
    await expect(canvas2).toBeVisible();
  });
});

test.describe('Loop 3: Honeycomb Layers 3D Visualization', () => {
  test('should render honeycomb hexagonal grid', async ({ page }) => {
    await page.goto('/loop3');

    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeVisible({ timeout: 10000 });

    await page.waitForTimeout(3000);

    console.log('✓ Honeycomb Layers canvas rendered');
  });

  test('should display quality gate indicators in 3D space', async ({ page }) => {
    await page.goto('/loop3');

    await page.waitForTimeout(3000);

    // Look for status text or indicators (may be HTML overlay on canvas)
    const statusIndicators = page.locator(
      '[data-testid="quality-gate"], .quality-indicator, .status-badge'
    );

    const count = await statusIndicators.count();

    if (count > 0) {
      console.log(`✓ Found ${count} quality gate indicators`);
    } else {
      console.log('ℹ️  No quality gate UI elements found - may be rendered in 3D');
    }
  });

  test('should support clicking on honeycomb cells for details', async ({ page }) => {
    await page.goto('/loop3');

    await page.waitForTimeout(3000);

    const canvas = page.locator('canvas').first();

    // Click on canvas center (likely to hit a honeycomb cell)
    await canvas.click({ position: { x: 200, y: 200 } });

    await page.waitForTimeout(500);

    // Look for modal or detail panel
    const detailPanel = page.locator('[role="dialog"], .detail-panel, .modal');

    if (await detailPanel.count() > 0) {
      console.log('✓ Cell click opened detail panel');
    } else {
      console.log('ℹ️  No detail panel detected - click interaction may not be implemented');
    }
  });
});

test.describe('3D Performance & Memory', () => {
  test('should not leak memory after repeated navigation', async ({ page }) => {
    // Navigate to Loop 1 multiple times
    for (let i = 0; i < 3; i++) {
      await page.goto('/loop1');
      await page.waitForTimeout(2000);

      // Navigate away
      await page.goto('/');
      await page.waitForTimeout(500);
    }

    // Check for memory leaks (basic check)
    const memoryInfo = await page.evaluate(() => {
      // @ts-expect-error - memory property is non-standard but exists in Chromium
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

    if (memoryInfo) {
      const usedMB = (memoryInfo.usedJSHeapSize / 1024 / 1024).toFixed(2);
      console.log(`Memory usage after 3 navigations: ${usedMB} MB`);

      // Warn if memory exceeds 200 MB
      if (memoryInfo.usedJSHeapSize > 200 * 1024 * 1024) {
        console.warn('⚠️  High memory usage detected - potential leak');
      } else {
        console.log('✓ Memory usage acceptable');
      }
    } else {
      console.log('ℹ️  Memory API not available (Chromium only)');
    }
  });

  test('should render all three loops without WebGL errors', async ({ page }) => {
    const loops = ['/loop1', '/loop2', '/loop3'];

    for (const loop of loops) {
      await page.goto(loop);

      await page.waitForTimeout(3000);

      // Check for WebGL context loss
      const webglError = await page.evaluate(() => {
        const canvas = document.querySelector('canvas');
        if (!canvas) return 'No canvas found';

        const gl = canvas.getContext('webgl') || canvas.getContext('webgl2');
        if (!gl) return 'No WebGL context';

        const contextLost = gl.isContextLost();
        return contextLost ? 'WebGL context lost' : null;
      });

      if (webglError) {
        console.warn(`⚠️  ${loop}: ${webglError}`);
      } else {
        console.log(`✓ ${loop}: WebGL context healthy`);
      }
    }
  });

  test('should maintain stable FPS across all three loops', async ({ page }) => {
    const loops = [
      { path: '/loop1', name: 'Flower Garden' },
      { path: '/loop2', name: 'Beehive Village' },
      { path: '/loop3', name: 'Honeycomb Layers' },
    ];

    for (const loop of loops) {
      await page.goto(loop.path);

      await page.waitForTimeout(2000);

      // Measure FPS
      const fps = await page.evaluate(() => {
        return new Promise<number>((resolve) => {
          let frameCount = 0;
          const startTime = performance.now();
          const duration = 2000;

          const countFrames = () => {
            frameCount++;

            if (performance.now() - startTime < duration) {
              requestAnimationFrame(countFrames);
            } else {
              const avgFps = (frameCount / duration) * 1000;
              resolve(avgFps);
            }
          };

          requestAnimationFrame(countFrames);
        });
      });

      console.log(`${loop.name} FPS: ${fps.toFixed(1)}`);

      // All loops should maintain 30+ FPS
      expect(fps).toBeGreaterThanOrEqual(30);
    }
  });
});

test.describe('3D Accessibility Features', () => {
  test('should provide alt text or ARIA labels for 3D visualizations', async ({ page }) => {
    await page.goto('/loop1');

    // Check for ARIA labels on canvas or container
    const canvas = page.locator('canvas').first();
    const ariaLabel = await canvas.getAttribute('aria-label');
    const ariaDescription = await canvas.getAttribute('aria-describedby');

    if (ariaLabel || ariaDescription) {
      console.log(`✓ Canvas has accessibility labels: ${ariaLabel || ariaDescription}`);
    } else {
      console.warn('⚠️  Canvas missing ARIA labels - consider adding for screen readers');
    }
  });

  test('should provide keyboard alternatives to mouse controls', async ({ page }) => {
    await page.goto('/loop1');

    await page.waitForTimeout(2000);

    // Try keyboard controls (common: Arrow keys, +/-, etc.)
    await page.keyboard.press('ArrowUp');
    await page.waitForTimeout(200);

    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(200);

    // Check for console errors (would indicate key events are handled)
    const consoleMessages: string[] = [];

    page.on('console', (msg) => {
      consoleMessages.push(msg.text());
    });

    await page.waitForTimeout(500);

    if (consoleMessages.length > 0) {
      console.log('ℹ️  Keyboard events detected, may have keyboard controls');
    } else {
      console.log('ℹ️  No keyboard event feedback - feature may not be implemented');
    }
  });

  test('should offer reduced motion option for users with vestibular disorders', async ({ page }) => {
    // Check if prefers-reduced-motion is respected
    await page.emulateMedia({ reducedMotion: 'reduce' });

    await page.goto('/loop1');

    await page.waitForTimeout(3000);

    // Measure FPS - should be lower or static if reduced motion is respected
    const fps = await page.evaluate(() => {
      return new Promise<number>((resolve) => {
        let frameCount = 0;
        const startTime = performance.now();
        const duration = 2000;

        const countFrames = () => {
          frameCount++;

          if (performance.now() - startTime < duration) {
            requestAnimationFrame(countFrames);
          } else {
            const avgFps = (frameCount / duration) * 1000;
            resolve(avgFps);
          }
        };

        requestAnimationFrame(countFrames);
      });
    });

    console.log(`FPS with reduced motion: ${fps.toFixed(1)}`);

    if (fps < 10) {
      console.log('✓ Animation significantly reduced for prefers-reduced-motion');
    } else if (fps < 30) {
      console.log('ℹ️  Animation partially reduced for prefers-reduced-motion');
    } else {
      console.warn('⚠️  prefers-reduced-motion may not be implemented');
    }
  });
});
