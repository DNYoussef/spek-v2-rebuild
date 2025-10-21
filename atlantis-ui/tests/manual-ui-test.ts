/**
 * Manual UI Testing Script with Chromium
 * Week 15 Day 1
 *
 * This script opens Chromium browser and navigates through all pages
 * to verify visual rendering and take screenshots.
 */

import { chromium, Browser, Page } from '@playwright/test';
import { promises as fs } from 'fs';
import path from 'path';

async function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function capturePageScreenshot(
  page: Page,
  url: string,
  name: string,
  screenshotsDir: string
) {
  console.log(`\n📸 Capturing: ${name}`);
  console.log(`   URL: ${url}`);

  await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
  await delay(1000); // Wait for any animations

  const screenshot = await page.screenshot({
    fullPage: true,
    path: path.join(screenshotsDir, `${name}.png`),
  });

  console.log(`   ✅ Saved: ${name}.png`);
  return screenshot;
}

async function main() {
  console.log('🚀 Starting Manual UI Test with Chromium...\n');

  // Create screenshots directory
  const screenshotsDir = path.join(__dirname, '../test-results/manual-screenshots');
  await fs.mkdir(screenshotsDir, { recursive: true });

  // Launch browser in headed mode (visible)
  console.log('🌐 Launching Chromium browser...');
  const browser: Browser = await chromium.launch({
    headless: false, // Show browser window
    slowMo: 500, // Slow down actions for visibility
  });

  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    deviceScaleFactor: 1,
  });

  const page = await context.newPage();

  // Test all 9 pages
  const pages = [
    { url: 'http://localhost:3002/', name: '01-homepage' },
    { url: 'http://localhost:3002/project/select', name: '02-project-select' },
    { url: 'http://localhost:3002/project/new', name: '03-project-new' },
    { url: 'http://localhost:3002/loop1', name: '04-loop1' },
    { url: 'http://localhost:3002/loop2', name: '05-loop2' },
    { url: 'http://localhost:3002/loop2/audit', name: '06-loop2-audit' },
    { url: 'http://localhost:3002/loop2/ui-review', name: '07-loop2-ui-review' },
    { url: 'http://localhost:3002/loop3', name: '08-loop3' },
    { url: 'http://localhost:3002/dashboard', name: '09-dashboard' },
  ];

  console.log(`\n📋 Testing ${pages.length} pages...\n`);
  console.log('═'.repeat(60));

  for (const pageInfo of pages) {
    try {
      await capturePageScreenshot(page, pageInfo.url, pageInfo.name, screenshotsDir);
      await delay(2000); // Pause between pages
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      console.error(`   ❌ Error: ${errorMessage}`);
    }
  }

  console.log('\n' + '═'.repeat(60));
  console.log('\n✅ Manual UI test complete!');
  console.log(`📁 Screenshots saved to: ${screenshotsDir}\n`);

  console.log('⏸️  Browser will stay open for 30 seconds for manual inspection...');
  await delay(30000);

  await browser.close();
  console.log('🔒 Browser closed.');
}

main().catch((error) => {
  console.error('❌ Fatal error:', error);
  process.exit(1);
});
