import { test, expect } from '@playwright/test';
import { captureWithRetry, disableAnimations } from './utils/screenshot-helper';

/**
 * Homepage E2E Tests
 * Week 15 Day 1 - Updated with research-backed screenshot capture
 */

test.describe('Homepage (Monarch Chat)', () => {
  test.beforeEach(async ({ page }) => {
    // Disable animations for consistent screenshots
    await page.goto('/');
    await disableAnimations(page);
  });

  test('should load homepage successfully', async ({ page }) => {
    await page.goto('/');

    // Check page title
    await expect(page).toHaveTitle(/SPEK/i);

    // Check main content is visible
    const heading = page.locator('h1');
    await expect(heading).toBeVisible();
    await expect(heading).toContainText(/SPEK Atlantis/i);

    // Check description
    await expect(page.locator('text=AI-Powered Agent Coordination Platform')).toBeVisible();

    // Check Monarch Chat section
    await expect(page.locator('text=Monarch Chat')).toBeVisible();
    await expect(
      page.locator('text=Interact with the Queen agent to orchestrate your project')
    ).toBeVisible();
  });

  test('should have functional chat interface', async ({ page }) => {
    await page.goto('/');

    // Check chat input exists
    const chatInput = page.locator('input[placeholder*="Ask Monarch"]');
    await expect(chatInput).toBeVisible();

    // Check send button exists
    const sendButton = page.locator('button:has-text("Send")');
    await expect(sendButton).toBeVisible();
  });

  test('should navigate to Loop 1 page', async ({ page }) => {
    await page.goto('/');

    // Find and click Loop 1 link (if exists)
    const loop1Link = page.locator('a[href="/loop1"]');
    if (await loop1Link.count() > 0) {
      await loop1Link.first().click();

      // Verify URL
      await expect(page).toHaveURL(/\/loop1/);
    }
  });

  test('should capture homepage screenshot with retry', async ({ page }) => {
    await captureWithRetry(page, {
      url: '/',
      screenshotName: 'homepage-monarch-chat.png',
      maxRetries: 3,
      has3DContent: false,
      waitForSelector: 'h1:has-text("SPEK Atlantis")',
    });
  });

  test('should have responsive layout', async ({ page }) => {
    await page.goto('/');

    // Check container max-width
    const container = page.locator('.max-w-4xl');
    await expect(container).toBeVisible();

    // Check min-height for main content
    const mainContent = page.locator('.min-h-\\[600px\\]');
    await expect(mainContent).toBeVisible();
  });
});
