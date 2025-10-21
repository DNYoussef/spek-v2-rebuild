#!/usr/bin/env node
/**
 * Accessibility Audit with axe-core
 * Week 19 Day 5
 *
 * Runs automated accessibility tests on Loop 1/2/3 pages
 */

const { chromium } = require('playwright');
const axe = require('axe-core');

async function runAccessibilityAudit() {
  console.log('🔍 Starting accessibility audit...\n');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const results = [];

  // Test pages
  const pages = [
    { name: 'Loop 1 Flower Garden', url: 'http://localhost:3000/loop1' },
    { name: 'Loop 2 Beehive Village', url: 'http://localhost:3000/loop2' },
    { name: 'Loop 3 Honeycomb Layers', url: 'http://localhost:3000/loop3' },
  ];

  for (const testPage of pages) {
    console.log(`Testing: ${testPage.name}`);

    try {
      await page.goto(testPage.url, { timeout: 30000, waitUntil: 'load' });
      await page.waitForTimeout(3000); // Wait for 3D to render

      // Inject axe-core and run audit
      await page.addScriptTag({ path: require.resolve('axe-core') });

      const result = await page.evaluate(async () => {
        const results = await axe.run();
        return {
          violations: results.violations.length,
          passes: results.passes.length,
          incomplete: results.incomplete.length,
          violationDetails: results.violations.map(v => ({
            id: v.id,
            impact: v.impact,
            description: v.description,
            nodes: v.nodes.length,
          })),
        };
      });

      results.push({
        page: testPage.name,
        ...result,
      });

      console.log(`  ✅ Passes: ${result.passes}`);
      console.log(`  ❌ Violations: ${result.violations}`);
      console.log(`  ⚠️  Incomplete: ${result.incomplete}\n`);

      if (result.violations > 0) {
        console.log('  Violation details:');
        result.violationDetails.forEach(v => {
          console.log(`    - ${v.id} (${v.impact}): ${v.description}`);
          console.log(`      ${v.nodes} element(s) affected`);
        });
        console.log('');
      }
    } catch (error) {
      console.error(`  ❌ Error testing ${testPage.name}:`, error.message);
    }
  }

  await browser.close();

  // Summary
  console.log('\n📊 Accessibility Audit Summary');
  console.log('================================');
  const totalViolations = results.reduce((sum, r) => sum + r.violations, 0);
  const totalPasses = results.reduce((sum, r) => sum + r.passes, 0);

  console.log(`Total Passes: ${totalPasses}`);
  console.log(`Total Violations: ${totalViolations}`);

  if (totalViolations === 0) {
    console.log('\n✅ All accessibility tests passed!');
  } else {
    console.log(`\n⚠️  ${totalViolations} accessibility violations found`);
    process.exit(1);
  }
}

runAccessibilityAudit().catch(console.error);
