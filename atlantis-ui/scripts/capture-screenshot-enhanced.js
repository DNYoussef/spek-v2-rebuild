/**
 * Enhanced Screenshot Capture Script for Week 18
 * Captures screenshots with better error handling and validation
 */

const playwright = require('playwright');
const fs = require('fs');
const path = require('path');

async function captureEnhancedScreenshots() {
  console.log('🚀 Launching Chromium for enhanced screenshot capture...');

  // Create screenshots directory if it doesn't exist
  const screenshotDir = path.join(__dirname, '..', 'tests', 'screenshots', 'week19');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
    console.log(`📁 Created directory: ${screenshotDir}`);
  }

  const browser = await playwright.chromium.launch({
    headless: false,
    slowMo: 500
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
  });

  const page = await context.newPage();

  const pages = [
    {
      name: 'homepage',
      url: 'http://localhost:3000',
      description: 'Homepage (Monarch Chat)',
      waitFor: 'h1', // Wait for heading
      delay: 2000
    },
    {
      name: 'loop1-flower-garden',
      url: 'http://localhost:3000/loop1',
      description: 'Loop 1 (Flower Garden) - NEW: Instanced pollen particles + FPS monitor',
      waitFor: 'canvas', // Wait for 3D canvas
      delay: 6000 // Extra time for 3D + particle rendering
    },
    {
      name: 'loop2-beehive-village',
      url: 'http://localhost:3000/loop2',
      description: 'Loop 2 (Beehive Village) - NEW: Accessibility + keyboard nav',
      waitFor: 'canvas',
      delay: 5000
    },
    {
      name: 'loop3-honeycomb-layers',
      url: 'http://localhost:3000/loop3',
      description: 'Loop 3 (Honeycomb Layers) - NEW: Accessibility + keyboard nav',
      waitFor: 'canvas',
      delay: 5000
    },
  ];

  let successCount = 0;
  let failCount = 0;

  for (const pageInfo of pages) {
    try {
      console.log(`\n📸 Capturing: ${pageInfo.description}`);
      console.log(`   URL: ${pageInfo.url}`);

      // Navigate with timeout (use domcontentloaded instead of networkidle)
      await page.goto(pageInfo.url, {
        waitUntil: 'domcontentloaded',
        timeout: 30000
      });

      // Wait for specific element
      console.log(`   Waiting for: ${pageInfo.waitFor}...`);
      await page.waitForSelector(pageInfo.waitFor, { timeout: 20000 }); // Increased for complex 3D scenes

      // Additional delay for rendering
      console.log(`   Waiting ${pageInfo.delay}ms for rendering...`);
      await page.waitForTimeout(pageInfo.delay);

      // Check if canvas is visible (for 3D pages)
      if (pageInfo.waitFor === 'canvas') {
        const canvasVisible = await page.evaluate(() => {
          const canvas = document.querySelector('canvas');
          if (!canvas) return false;
          const rect = canvas.getBoundingClientRect();
          return rect.width > 0 && rect.height > 0;
        });

        if (!canvasVisible) {
          console.log('   ⚠️  Warning: Canvas found but not visible');
        } else {
          console.log('   ✅ Canvas visible and ready');
        }
      }

      // Capture screenshot
      const screenshotPath = path.join(screenshotDir, `${pageInfo.name}.png`);
      await page.screenshot({
        path: screenshotPath,
        fullPage: true,
      });

      // Verify screenshot was created
      if (fs.existsSync(screenshotPath)) {
        const stats = fs.statSync(screenshotPath);
        console.log(`   ✅ Screenshot saved (${Math.round(stats.size / 1024)} KB)`);
        successCount++;
      } else {
        console.log('   ❌ Screenshot file not created');
        failCount++;
      }

    } catch (error) {
      console.error(`   ❌ Error capturing ${pageInfo.name}:`, error.message);
      failCount++;
    }
  }

  await browser.close();

  // Print summary
  console.log('\n' + '━'.repeat(60));
  console.log('📊 Screenshot Capture Summary');
  console.log('━'.repeat(60));
  console.log(`✅ Successful: ${successCount}/${pages.length}`);
  console.log(`❌ Failed:     ${failCount}/${pages.length}`);
  console.log(`📁 Location:   ${screenshotDir}`);
  console.log('━'.repeat(60));

  if (successCount === pages.length) {
    console.log('\n🎉 All screenshots captured successfully!');
  } else {
    console.log(`\n⚠️  ${failCount} screenshot(s) failed. Check errors above.`);
  }
}

captureEnhancedScreenshots().catch(console.error);
