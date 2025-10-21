/**
 * FPS Measurement Script for Week 18
 * Measures frames per second on all 3 loop visualizations
 */

const playwright = require('playwright');

async function measureFPS() {
  console.log('🚀 Launching browser for FPS measurement...');
  const browser = await playwright.chromium.launch({
    headless: false,
    args: ['--enable-precise-memory-info'] // Enable GPU memory tracking
  });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
  });
  const page = await context.newPage();

  const loops = [
    { name: 'Loop 1 (Flower Garden)', url: 'http://localhost:3001/loop1' },
    { name: 'Loop 2 (Beehive Village)', url: 'http://localhost:3001/loop2' },
    { name: 'Loop 3 (Honeycomb Layers)', url: 'http://localhost:3001/loop3' },
  ];

  const results = [];

  try {
    for (const { name, url } of loops) {
      console.log(`\n📊 Measuring FPS for ${name}...`);
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });

      // Wait for 3D scene to load
      await page.waitForSelector('canvas', { timeout: 10000 });
      await page.waitForTimeout(3000); // Let scene initialize

      // Measure FPS over 10 seconds
      const metrics = await page.evaluate(() => {
        return new Promise((resolve) => {
          let frameCount = 0;
          const startTime = performance.now();
          const duration = 10000; // 10 seconds
          const fpsReadings = [];

          function countFrame() {
            frameCount++;
            const elapsed = performance.now() - startTime;

            // Record FPS every second
            if (frameCount % 60 === 0) {
              const currentFPS = Math.round((frameCount / elapsed) * 1000);
              fpsReadings.push(currentFPS);
            }

            if (elapsed < duration) {
              requestAnimationFrame(countFrame);
            } else {
              const avgFPS = Math.round((frameCount / elapsed) * 1000);
              const minFPS = Math.min(...fpsReadings);
              const maxFPS = Math.max(...fpsReadings);

              resolve({
                avgFPS,
                minFPS,
                maxFPS,
                frameCount,
                duration: Math.round(elapsed)
              });
            }
          }

          requestAnimationFrame(countFrame);
        });
      });

      results.push({ name, ...metrics });
      console.log(`  Average FPS: ${metrics.avgFPS}`);
      console.log(`  Min FPS: ${metrics.minFPS}`);
      console.log(`  Max FPS: ${metrics.maxFPS}`);
      console.log(`  Frames rendered: ${metrics.frameCount}`);
      console.log(`  Duration: ${metrics.duration}ms`);
    }

    // Print summary
    console.log('\n📊 FPS Results Summary:');
    console.log('━'.repeat(60));
    console.log('Loop Name                  | Avg  | Min  | Max  | Status');
    console.log('━'.repeat(60));

    results.forEach(({ name, avgFPS, minFPS, maxFPS }) => {
      const status = avgFPS >= 60 ? '✅ EXCELLENT' :
                     avgFPS >= 45 ? '🔶 GOOD' :
                     avgFPS >= 30 ? '⚠️  ACCEPTABLE' :
                                    '❌ POOR';

      const namePadded = name.padEnd(26);
      const avgPadded = String(avgFPS).padStart(4);
      const minPadded = String(minFPS).padStart(4);
      const maxPadded = String(maxFPS).padStart(4);

      console.log(`${namePadded} | ${avgPadded} | ${minPadded} | ${maxPadded} | ${status}`);
    });

    console.log('━'.repeat(60));
    console.log('\n🎯 Performance Targets:');
    console.log('  Desktop: ≥60 FPS (EXCELLENT)');
    console.log('  Mobile:  ≥30 FPS (ACCEPTABLE)');

    // Check if all loops meet targets
    const allPassDesktop = results.every(r => r.avgFPS >= 60);
    if (allPassDesktop) {
      console.log('\n✅ All loops meet desktop FPS target (60 FPS)!');
    } else {
      const failedLoops = results.filter(r => r.avgFPS < 60);
      console.log(`\n⚠️  ${failedLoops.length} loop(s) below desktop target:`);
      failedLoops.forEach(({ name, avgFPS }) => {
        console.log(`  - ${name}: ${avgFPS} FPS`);
      });
    }

  } catch (error) {
    console.error('\n❌ Error measuring FPS:', error.message);
  } finally {
    await browser.close();
  }

  return results;
}

measureFPS().catch(console.error);
