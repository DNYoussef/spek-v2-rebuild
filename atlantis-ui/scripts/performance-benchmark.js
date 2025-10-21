#!/usr/bin/env node
/**
 * Performance Benchmarking Script
 * Week 19 Day 7
 *
 * Measures load times, FPS, memory usage for all Loop pages
 */

const { chromium } = require('playwright');

async function runPerformanceBenchmark() {
  console.log('🚀 Starting performance benchmark...\n');

  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  const results = [];

  const pages = [
    { name: 'Homepage', url: 'http://localhost:3000' },
    { name: 'Loop 1 Flower Garden', url: 'http://localhost:3000/loop1' },
    { name: 'Loop 2 Beehive Village', url: 'http://localhost:3000/loop2' },
    { name: 'Loop 3 Honeycomb Layers', url: 'http://localhost:3000/loop3' },
  ];

  for (const testPage of pages) {
    console.log(`Benchmarking: ${testPage.name}`);

    try {
      const startTime = Date.now();

      // Navigate and measure load time
      await page.goto(testPage.url, { timeout: 30000, waitUntil: 'load' });
      const loadTime = Date.now() - startTime;

      // Wait for 3D to initialize
      await page.waitForTimeout(3000);

      // Measure FPS
      const fpsData = await page.evaluate(() => {
        return new Promise((resolve) => {
          let frameCount = 0;
          const startTime = performance.now();
          const duration = 5000; // 5 seconds

          function countFrames() {
            frameCount++;
            const elapsed = performance.now() - startTime;

            if (elapsed < duration) {
              requestAnimationFrame(countFrames);
            } else {
              const fps = (frameCount / elapsed) * 1000;
              resolve({
                fps: Math.round(fps),
                frameCount,
                duration: Math.round(elapsed),
              });
            }
          }

          requestAnimationFrame(countFrames);
        });
      });

      // Measure memory
      const memoryData = await page.evaluate(() => {
        if (performance.memory) {
          const mem = performance.memory;
          return {
            usedJSHeapSize: Math.round(mem.usedJSHeapSize / 1024 / 1024),
            totalJSHeapSize: Math.round(mem.totalJSHeapSize / 1024 / 1024),
            jsHeapSizeLimit: Math.round(mem.jsHeapSizeLimit / 1024 / 1024),
          };
        }
        return null;
      });

      results.push({
        page: testPage.name,
        loadTime,
        fps: fpsData.fps,
        frameCount: fpsData.frameCount,
        memory: memoryData,
      });

      console.log(`  ⏱️  Load Time: ${loadTime}ms`);
      console.log(`  📊 FPS: ${fpsData.fps} (${fpsData.frameCount} frames in ${fpsData.duration}ms)`);
      if (memoryData) {
        console.log(`  💾 Memory: ${memoryData.usedJSHeapSize}MB / ${memoryData.totalJSHeapSize}MB`);
      }
      console.log('');
    } catch (error) {
      console.error(`  ❌ Error benchmarking ${testPage.name}:`, error.message);
    }
  }

  await browser.close();

  // Summary
  console.log('\n📊 Performance Benchmark Summary');
  console.log('==================================');

  const avgLoadTime = results.reduce((sum, r) => sum + r.loadTime, 0) / results.length;
  const avgFPS = results.reduce((sum, r) => sum + r.fps, 0) / results.length;
  const avgMemory = results
    .filter(r => r.memory)
    .reduce((sum, r) => sum + r.memory.usedJSHeapSize, 0) /
    results.filter(r => r.memory).length;

  console.log(`Average Load Time: ${Math.round(avgLoadTime)}ms`);
  console.log(`Average FPS: ${Math.round(avgFPS)}`);
  console.log(`Average Memory: ${Math.round(avgMemory)}MB`);

  // Targets
  console.log('\n🎯 Performance Targets:');
  console.log(`  Load Time: ${avgLoadTime < 2000 ? '✅' : '❌'} ${Math.round(avgLoadTime)}ms (target: <2000ms)`);
  console.log(`  FPS (Desktop): ${avgFPS >= 60 ? '✅' : '⚠️'} ${Math.round(avgFPS)} (target: 60 FPS)`);
  console.log(`  Memory: ${avgMemory < 500 ? '✅' : '⚠️'} ${Math.round(avgMemory)}MB (target: <500MB)`);

  // Overall assessment
  const passedTargets = [
    avgLoadTime < 2000,
    avgFPS >= 55, // Allow 5 FPS margin
    avgMemory < 500,
  ].filter(Boolean).length;

  console.log(`\n${passedTargets === 3 ? '✅' : '⚠️'} Performance Score: ${passedTargets}/3 targets met`);
}

runPerformanceBenchmark().catch(console.error);
