#!/usr/bin/env node
/**
 * Automated ESLint Fix Script
 *
 * Fixes common ESLint issues across the codebase:
 * 1. Unused error parameters (prefix with _)
 * 2. Add descriptions to @ts-expect-error directives
 * 3. Replace @ts-ignore with @ts-expect-error
 *
 * Week 24: ESLint Full Compliance
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔧 Starting automated ESLint fixes...\n');

// Get list of files with ESLint issues
console.log('📋 Getting list of files with issues...');
const eslintOutput = execSync('npx eslint . --ext .ts,.tsx --format json', {
  encoding: 'utf-8',
  stdio: ['pipe', 'pipe', 'ignore'],
});

const results = JSON.parse(eslintOutput);
const filesWithIssues = results.filter(r => r.errorCount > 0 || r.warningCount > 0);

console.log(`Found ${filesWithIssues.length} files with issues\n`);

let totalFixed = 0;

filesWithIssues.forEach(fileResult => {
  const filePath = fileResult.filePath;
  const relativePath = path.relative(process.cwd(), filePath);

  console.log(`\n📝 Processing: ${relativePath}`);

  let content = fs.readFileSync(filePath, 'utf-8');
  let originalContent = content;
  let fixCount = 0;

  // Fix 1: Unused error parameters - prefix with underscore
  const unusedErrorMatches = fileResult.messages.filter(m =>
    m.message.includes("'error' is defined but never used") ||
    m.message.includes("'e' is defined but never used")
  );

  unusedErrorMatches.forEach(match => {
    const lines = content.split('\n');
    const line = lines[match.line - 1];

    if (line && line.includes('catch')) {
      // Replace (error) with (_error) or (e) with (_e)
      const newLine = line.replace(/catch\s*\(\s*error\s*\)/, 'catch (_error)')
                          .replace(/catch\s*\(\s*e\s*\)/, 'catch (_e)');

      if (newLine !== line) {
        lines[match.line - 1] = newLine;
        content = lines.join('\n');
        fixCount++;
        console.log(`  ✓ Fixed unused error parameter on line ${match.line}`);
      }
    }
  });

  // Fix 2: Add descriptions to @ts-expect-error
  const tsExpectErrorMatches = fileResult.messages.filter(m =>
    m.message.includes('Include a description after the "@ts-expect-error"')
  );

  tsExpectErrorMatches.forEach(match => {
    const lines = content.split('\n');
    const line = lines[match.line - 1];

    if (line && line.includes('@ts-expect-error') && !line.includes('@ts-expect-error -')) {
      // Check context to determine appropriate description
      const nextLine = lines[match.line] || '';
      let description = 'Non-standard API';

      if (nextLine.includes('performance.memory')) {
        description = 'Non-standard browser API (performance.memory) only available in Chromium';
      } else if (nextLine.includes('usedJSHeapSize') || nextLine.includes('totalJSHeapSize')) {
        description = 'Non-standard performance memory properties';
      }

      const newLine = line.replace('@ts-expect-error', `@ts-expect-error - ${description}`);

      if (newLine !== line) {
        lines[match.line - 1] = newLine;
        content = lines.join('\n');
        fixCount++;
        console.log(`  ✓ Added description to @ts-expect-error on line ${match.line}`);
      }
    }
  });

  // Fix 3: Replace @ts-ignore with @ts-expect-error
  const tsIgnoreMatches = fileResult.messages.filter(m =>
    m.message.includes('Use "@ts-expect-error" instead of "@ts-ignore"')
  );

  tsIgnoreMatches.forEach(match => {
    const lines = content.split('\n');
    const line = lines[match.line - 1];

    if (line && line.includes('@ts-ignore')) {
      const newLine = line.replace('@ts-ignore', '@ts-expect-error - Type assertion needed');

      if (newLine !== line) {
        lines[match.line - 1] = newLine;
        content = lines.join('\n');
        fixCount++;
        console.log(`  ✓ Replaced @ts-ignore with @ts-expect-error on line ${match.line}`);
      }
    }
  });

  // Write back if changed
  if (content !== originalContent) {
    fs.writeFileSync(filePath, content, 'utf-8');
    totalFixed += fixCount;
    console.log(`  💾 Saved ${fixCount} fixes`);
  } else {
    console.log(`  ⏭️  No automatic fixes available`);
  }
});

console.log(`\n\n✅ Automated fixes complete!`);
console.log(`📊 Total fixes applied: ${totalFixed}`);
console.log(`\n🔍 Run 'npx eslint . --ext .ts,.tsx' to see remaining issues\n`);
