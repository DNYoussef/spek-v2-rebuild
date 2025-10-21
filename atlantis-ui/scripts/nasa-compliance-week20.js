#!/usr/bin/env node
/**
 * Week 20 Day 5: NASA Rule 10 Compliance Check
 *
 * Checks all Week 20 Context DNA TypeScript files for NASA Rule 10:
 * - Functions must be ≤60 lines of code
 * - Target: ≥92% compliance
 */

const fs = require('fs');
const path = require('path');

const NASA_LIMIT = 60;
const TARGET_COMPLIANCE = 92;

class NASAComplianceChecker {
  constructor() {
    this.results = {
      totalFunctions: 0,
      compliantFunctions: 0,
      violations: [],
      fileStats: {},
    };
  }

  /**
   * Count function LOC in a TypeScript file
   */
  analyzeFunctionLengths(filePath) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n');

    const functions = [];
    let inFunction = false;
    let functionName = '';
    let functionStart = 0;
    let braceCount = 0;
    let functionLines = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();

      // Skip comments and empty lines
      if (trimmed.startsWith('//') || trimmed.startsWith('/*') || trimmed.startsWith('*') || trimmed === '') {
        continue;
      }

      // Detect function start
      if (!inFunction) {
        // Match: async functionName(...) { or private functionName(...) {
        const funcMatch = trimmed.match(/(?:async\s+)?(?:private\s+|public\s+|protected\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*[^{]+)?\s*\{/);
        if (funcMatch) {
          functionName = funcMatch[1];
          functionStart = i + 1; // Line numbers start at 1
          braceCount = 1;
          inFunction = true;
          functionLines = [line];
          continue;
        }
      }

      // Track braces inside function
      if (inFunction) {
        functionLines.push(line);

        // Count opening and closing braces
        for (const char of line) {
          if (char === '{') braceCount++;
          if (char === '}') braceCount--;
        }

        // Function end
        if (braceCount === 0) {
          // Count non-empty, non-comment lines
          const nonEmptyLines = functionLines.filter(l => {
            const t = l.trim();
            return t !== '' && !t.startsWith('//') && !t.startsWith('/*') && !t.startsWith('*');
          });

          const loc = nonEmptyLines.length;
          const functionEnd = i + 1;

          functions.push({
            name: functionName,
            start: functionStart,
            end: functionEnd,
            loc,
            compliant: loc <= NASA_LIMIT,
          });

          inFunction = false;
          functionName = '';
          functionLines = [];
        }
      }
    }

    return functions;
  }

  /**
   * Analyze all Week 20 files
   */
  analyzeWeek20Files() {
    const contextDnaDir = path.join(process.cwd(), 'src', 'services', 'context-dna');
    const files = fs.readdirSync(contextDnaDir)
      .filter(f => f.endsWith('.ts') && f !== 'types.ts' && !f.endsWith('.test.ts'))
      .map(f => path.join(contextDnaDir, f));

    console.log('📊 NASA Rule 10 Compliance Check (Week 20)\n');
    console.log(`Target: Functions ≤${NASA_LIMIT} LOC, ≥${TARGET_COMPLIANCE}% compliance\n`);
    console.log('='.repeat(70));

    for (const filePath of files) {
      const fileName = path.basename(filePath);
      const functions = this.analyzeFunctionLengths(filePath);

      if (functions.length === 0) continue;

      const compliant = functions.filter(f => f.compliant).length;
      const complianceRate = (compliant / functions.length) * 100;

      this.results.fileStats[fileName] = {
        totalFunctions: functions.length,
        compliantFunctions: compliant,
        complianceRate,
      };

      console.log(`\n📄 ${fileName}`);
      console.log(`   Functions: ${functions.length}, Compliant: ${compliant}/${functions.length} (${complianceRate.toFixed(1)}%)`);

      for (const func of functions) {
        this.results.totalFunctions++;
        if (func.compliant) {
          this.results.compliantFunctions++;
        } else {
          this.results.violations.push({
            file: fileName,
            function: func.name,
            loc: func.loc,
            lines: `${func.start}-${func.end}`,
          });
          console.log(`   ❌ ${func.name} (${func.start}-${func.end}): ${func.loc} LOC (${func.loc - NASA_LIMIT} over)`);
        }
      }
    }

    this.generateReport();
  }

  /**
   * Generate compliance report
   */
  generateReport() {
    console.log('\n' + '='.repeat(70));
    console.log('📊 WEEK 20 NASA RULE 10 COMPLIANCE REPORT');
    console.log('='.repeat(70));

    const overallCompliance = (this.results.compliantFunctions / this.results.totalFunctions) * 100;

    console.log(`\n✅ OVERALL COMPLIANCE: ${overallCompliance.toFixed(1)}%`);
    console.log(`   Total Functions: ${this.results.totalFunctions}`);
    console.log(`   Compliant: ${this.results.compliantFunctions}`);
    console.log(`   Violations: ${this.results.violations.length}`);

    if (this.results.violations.length > 0) {
      console.log(`\n❌ VIOLATIONS (${this.results.violations.length} total):`);
      for (const v of this.results.violations) {
        console.log(`   ${v.file} :: ${v.function} (lines ${v.lines}): ${v.loc} LOC`);
      }
    }

    const status = overallCompliance >= TARGET_COMPLIANCE ? '✅ PASS' : '⚠️ NEEDS WORK';
    console.log(`\n${status}: Target is ≥${TARGET_COMPLIANCE}%, actual is ${overallCompliance.toFixed(1)}%`);

    console.log('\n' + '='.repeat(70));
  }
}

// Run compliance check
if (require.main === module) {
  const checker = new NASAComplianceChecker();
  checker.analyzeWeek20Files();
}

module.exports = { NASAComplianceChecker };
