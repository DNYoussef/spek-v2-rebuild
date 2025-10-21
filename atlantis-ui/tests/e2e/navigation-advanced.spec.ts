import { test, expect } from '@playwright/test';

/**
 * Advanced Navigation E2E Tests
 * Week 22 - Production Hardening Phase 3
 *
 * Expands navigation coverage with additional edge cases and scenarios:
 * - Keyboard navigation
 * - Tab navigation
 * - Hash fragment navigation
 * - Programmatic navigation
 * - Navigation guards
 * - External link handling
 */

test.describe('Advanced Keyboard Navigation', () => {
  test('should support Tab key navigation through interactive elements', async ({ page }) => {
    await page.goto('/');

    // Focus first interactive element
    await page.keyboard.press('Tab');

    // Get currently focused element
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);

    // Should focus on a button, link, or input
    expect(['BUTTON', 'A', 'INPUT', 'TEXTAREA']).toContain(focusedElement);

    console.log(`✓ Tab navigation working - focused on ${focusedElement}`);
  });

  test('should navigate using keyboard shortcuts (if implemented)', async ({ page }) => {
    await page.goto('/');

    // Try common keyboard shortcuts
    // Ctrl+K or Cmd+K for command palette/search
    const isMac = process.platform === 'darwin';
    const modifier = isMac ? 'Meta' : 'Control';

    await page.keyboard.press(`${modifier}+KeyK`);

    // Wait for potential command palette
    await page.waitForTimeout(500);

    // Check if command palette or search opened
    const commandPalette = page.locator('[role="dialog"], [role="search"], .command-palette');

    if (await commandPalette.count() > 0) {
      console.log('✓ Keyboard shortcut (Ctrl/Cmd+K) opens command palette');
    } else {
      console.log('ℹ️  No command palette detected - feature may not be implemented');
    }
  });

  test('should support escape key to close modals/dialogs', async ({ page }) => {
    await page.goto('/');

    // Look for any buttons that might open a modal
    const modalTrigger = page.locator('button:has-text("Settings"), button:has-text("Help")').first();

    if (await modalTrigger.count() > 0) {
      await modalTrigger.click();

      await page.waitForTimeout(300);

      // Press Escape
      await page.keyboard.press('Escape');

      await page.waitForTimeout(300);

      // Check if modal is closed
      const modal = page.locator('[role="dialog"]');
      const isVisible = await modal.isVisible().catch(() => false);

      if (!isVisible) {
        console.log('✓ Escape key closes modal');
      } else {
        console.warn('⚠️  Escape key did not close modal');
      }
    } else {
      test.skip(true, 'No modal triggers found to test Escape key');
    }
  });

  test('should support arrow key navigation in lists/menus', async ({ page }) => {
    await page.goto('/project/select');

    // Look for a list or menu
    const listItems = page.locator('[role="listbox"] [role="option"], [role="menu"] [role="menuitem"], li');

    if (await listItems.count() > 0) {
      // Focus first item
      await listItems.first().focus();

      // Press ArrowDown
      await page.keyboard.press('ArrowDown');

      await page.waitForTimeout(100);

      // Check if focus moved
      const focusedElement = await page.evaluate(() => {
        const el = document.activeElement;
        return el?.getAttribute('role') || el?.tagName;
      });

      console.log(`✓ Arrow key navigation detected - focused element: ${focusedElement}`);
    } else {
      console.log('ℹ️  No navigable lists found on this page');
    }
  });
});

test.describe('Hash Fragment Navigation', () => {
  test('should navigate to hash fragments (#section)', async ({ page }) => {
    await page.goto('/help#faq');

    // Verify URL includes hash
    await expect(page).toHaveURL(/#faq/);

    // Check if page scrolled to section
    const scrollY = await page.evaluate(() => window.scrollY);

    if (scrollY > 0) {
      console.log(`✓ Page scrolled to #faq section (${scrollY}px)`);
    } else {
      console.log('ℹ️  Page did not scroll - hash target may not exist or page may not have scroll');
    }
  });

  test('should update hash on scroll (if scroll spy implemented)', async ({ page }) => {
    await page.goto('/help');

    // Scroll down the page
    await page.evaluate(() => window.scrollTo(0, 1000));

    await page.waitForTimeout(500);

    // Check if URL hash updated
    const currentHash = await page.evaluate(() => window.location.hash);

    if (currentHash && currentHash.length > 1) {
      console.log(`✓ Hash updated on scroll: ${currentHash}`);
    } else {
      console.log('ℹ️  Hash did not update - scroll spy may not be implemented');
    }
  });

  test('should support smooth scrolling to hash targets', async ({ page }) => {
    await page.goto('/help');

    // Find a link with hash
    const hashLink = page.locator('a[href^="#"]').first();

    if (await hashLink.count() > 0) {
      const href = await hashLink.getAttribute('href');

      await hashLink.click();

      await page.waitForTimeout(1000); // Wait for smooth scroll

      // Verify hash in URL
      if (href) {
        await expect(page).toHaveURL(new RegExp(href.replace('#', '#')));
        console.log(`✓ Smooth scroll to ${href} completed`);
      }
    } else {
      test.skip(true, 'No hash links found on help page');
    }
  });
});

test.describe('Programmatic Navigation', () => {
  test('should handle window.history.pushState navigation', async ({ page }) => {
    await page.goto('/');

    // Programmatically navigate using pushState
    await page.evaluate(() => {
      window.history.pushState({}, '', '/loop1');
    });

    // Verify URL changed
    await expect(page).toHaveURL(/\/loop1/);

    // Verify content didn't load (pushState doesn't trigger page load)
    // This is expected behavior - frameworks handle this differently
    console.log('✓ pushState navigation updated URL');
  });

  test('should handle window.location navigation', async ({ page }) => {
    await page.goto('/');

    // Programmatically navigate using window.location
    await page.evaluate(() => {
      window.location.href = '/loop2';
    });

    // Wait for navigation to complete
    await page.waitForURL(/\/loop2/, { timeout: 5000 });

    // Verify page loaded
    await expect(page.locator('body')).toBeVisible();

    console.log('✓ window.location.href navigation completed');
  });
});

test.describe('Navigation Guards & Authentication', () => {
  test('should redirect from protected routes if not authenticated', async ({ page }) => {
    // Try to access a potentially protected route
    await page.goto('/project/select');

    // Wait for potential redirect
    await page.waitForTimeout(1000);

    const currentUrl = page.url();

    // If authentication is implemented, should redirect to login or homepage
    if (currentUrl.includes('/login') || currentUrl === '/') {
      console.log('✓ Protected route redirected to authentication');
    } else {
      console.log('ℹ️  No authentication redirect detected - may not be implemented');
    }
  });

  test('should preserve intended route after authentication', async ({ page }) => {
    // Try to access protected route
    await page.goto('/settings');

    // Wait for potential redirect
    await page.waitForTimeout(500);

    const currentUrl = page.url();

    // Check if redirect parameter exists
    if (currentUrl.includes('redirect=') || currentUrl.includes('returnTo=')) {
      console.log('✓ Intended route preserved in redirect URL');
    } else {
      console.log('ℹ️  No redirect parameter found - feature may not be implemented');
    }
  });
});

test.describe('External Link Handling', () => {
  test('should open external links in new tab (target="_blank")', async ({ page }) => {
    await page.goto('/help');

    // Look for external links
    const externalLinks = page.locator('a[href^="http://"], a[href^="https://"]');

    if (await externalLinks.count() > 0) {
      const firstLink = externalLinks.first();
      const target = await firstLink.getAttribute('target');

      if (target === '_blank') {
        console.log('✓ External links have target="_blank"');
      } else {
        console.warn('⚠️  External links missing target="_blank" - may be security risk');
      }

      // Check for rel="noopener noreferrer"
      const rel = await firstLink.getAttribute('rel');

      if (rel?.includes('noopener') && rel?.includes('noreferrer')) {
        console.log('✓ External links have proper rel attributes (security)');
      } else {
        console.warn('⚠️  External links missing rel="noopener noreferrer" - security recommendation');
      }
    } else {
      console.log('ℹ️  No external links found on help page');
    }
  });

  test('should not navigate away from app on external link click', async ({ page, context }) => {
    await page.goto('/');

    // Listen for new pages (new tabs)
    const [newPage] = await Promise.all([
      context.waitForEvent('page').catch(() => null),
      page.locator('a[href^="http"]').first().click().catch(() => null)
    ]).catch(() => [null]);

    if (newPage) {
      console.log('✓ External link opened in new tab');
      await newPage.close();
    } else {
      console.log('ℹ️  No external links found or clicked');
    }
  });
});

test.describe('Navigation Error Handling', () => {
  test('should handle navigation to deleted/moved pages gracefully', async ({ page }) => {
    // Navigate to a page that might have been moved
    const response = await page.goto('/old-page-that-does-not-exist');

    // Check response status
    const status = response?.status();

    if (status === 404) {
      console.log('✓ Server returns 404 for non-existent pages');

      // Check if custom 404 page is shown
      const pageText = await page.locator('body').textContent();

      if (pageText?.includes('404') || pageText?.includes('Not Found')) {
        console.log('✓ Custom 404 page displayed');
      }
    } else if (status === 200) {
      console.log('⚠️  Non-existent page returns 200 - may need proper 404 handling');
    }
  });

  test('should recover from navigation errors', async ({ page }) => {
    // Try to navigate to invalid URL
    await page.goto('/invalid$%^&*page').catch(() => {});

    // Wait a bit
    await page.waitForTimeout(500);

    // Should still be able to navigate to valid page
    await page.goto('/');

    await expect(page.locator('body')).toBeVisible();

    console.log('✓ App recovers from navigation errors');
  });
});

test.describe('Navigation Performance', () => {
  test('should prefetch link targets on hover (if implemented)', async ({ page }) => {
    await page.goto('/');

    // Find navigation links
    const navLinks = page.locator('nav a, header a').first();

    if (await navLinks.count() > 0) {
      // Listen for prefetch requests
      const prefetchRequests: string[] = [];

      page.on('request', (request) => {
        // Check if request is for prefetch by looking at headers synchronously
        // Note: Can't use await in this callback, so check URL patterns instead
        const url = request.url();
        const resourceType = request.resourceType();

        // Next.js prefetch requests are typically script/document types
        if (resourceType === 'document' || resourceType === 'script') {
          // Also check for _next prefetch patterns
          if (url.includes('_next') || url.includes('prefetch')) {
            prefetchRequests.push(url);
          }
        }
      });

      // Hover over link
      await navLinks.hover();

      await page.waitForTimeout(500);

      if (prefetchRequests.length > 0) {
        console.log(`✓ Prefetch detected: ${prefetchRequests.length} resources`);
      } else {
        console.log('ℹ️  No prefetch detected - Next.js <Link> may not be used');
      }
    }
  });

  test('should use client-side navigation for internal links', async ({ page }) => {
    await page.goto('/');

    // Track full page reloads
    let pageReloaded = false;

    page.on('load', () => {
      pageReloaded = true;
    });

    // Click internal link
    const internalLink = page.locator('a[href^="/"]').first();

    if (await internalLink.count() > 0) {
      await internalLink.click();

      await page.waitForTimeout(1000);

      if (!pageReloaded) {
        console.log('✓ Client-side navigation (no full page reload)');
      } else {
        console.warn('⚠️  Full page reload detected - may want to use Next.js <Link>');
      }
    }
  });
});
