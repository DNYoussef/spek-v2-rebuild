/**
 * Simple screenshot capture script for Week 17 validation
 */

const playwright = require('playwright');

async function captureScreenshots() {
  console.log('🚀 Launching browser...');
  const browser = await playwright.chromium.launch({
    headless: false, // Open visible window
    slowMo: 500 // Slow down for debugging
  });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
  });
  const page = await context.newPage();

  try {
    // Homepage
    console.log('📸 Capturing homepage...');
    await page.goto('http://localhost:3001', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000); // Wait for page to settle
    await page.screenshot({ path: 'tests/screenshots/week17-homepage.png', fullPage: true });
    console.log('✅ Homepage screenshot saved');

    // Loop 1 - Flower Garden
    console.log('📸 Capturing Loop 1 (Flower Garden)...');
    await page.goto('http://localhost:3001/loop1', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000); // Wait for 3D to render
    await page.screenshot({ path: 'tests/screenshots/week17-loop1-flower-garden.png', fullPage: true });
    console.log('✅ Loop 1 screenshot saved');

    // Loop 2 - Beehive Village
    console.log('📸 Capturing Loop 2 (Beehive Village)...');
    await page.goto('http://localhost:3001/loop2', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000); // Wait for 3D to render
    await page.screenshot({ path: 'tests/screenshots/week17-loop2-beehive-village.png', fullPage: true });
    console.log('✅ Loop 2 screenshot saved');

    // Loop 3 - Honeycomb Layers
    console.log('📸 Capturing Loop 3 (Honeycomb Layers)...');
    await page.goto('http://localhost:3001/loop3', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000); // Wait for 3D to render
    await page.screenshot({ path: 'tests/screenshots/week17-loop3-honeycomb-layers.png', fullPage: true });
    console.log('✅ Loop 3 screenshot saved');

    console.log('\n✅ All screenshots captured successfully!');
    console.log('📁 Screenshots location: tests/screenshots/');
  } catch (error) {
    console.error('❌ Error capturing screenshots:', error.message);
  } finally {
    await browser.close();
  }
}

captureScreenshots();
