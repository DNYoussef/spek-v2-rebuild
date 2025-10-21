/**
 * NASA Rule 10 Compliance Checker for Week 17 Code
 *
 * Validates that all functions are ≤60 lines of code
 * Target: ≥95% compliance (allow up to 5% violations)
 */

import * as ts from 'typescript';
import * as fs from 'fs';
import * as path from 'path';

interface FunctionMetrics {
  name: string;
  file: string;
  startLine: number;
  endLine: number;
  lineCount: number;
  compliant: boolean;
}

function checkFile(filePath: string): FunctionMetrics[] {
  const sourceCode = fs.readFileSync(filePath, 'utf-8');
  const sourceFile = ts.createSourceFile(
    filePath,
    sourceCode,
    ts.ScriptTarget.Latest,
    true
  );

  const metrics: FunctionMetrics[] = [];

  function visit(node: ts.Node) {
    if (
      ts.isFunctionDeclaration(node) ||
      ts.isMethodDeclaration(node) ||
      ts.isArrowFunction(node) ||
      ts.isFunctionExpression(node)
    ) {
      const start = sourceFile.getLineAndCharacterOfPosition(node.getStart());
      const end = sourceFile.getLineAndCharacterOfPosition(node.getEnd());
      const lineCount = end.line - start.line + 1;

      let name = '<anonymous>';
      if (ts.isFunctionDeclaration(node) || ts.isMethodDeclaration(node)) {
        name = node.name?.getText(sourceFile) || '<anonymous>';
      } else {
        name = '<arrow>';
      }

      metrics.push({
        name,
        file: path.basename(filePath),
        startLine: start.line + 1,
        endLine: end.line + 1,
        lineCount,
        compliant: lineCount <= 60,
      });
    }

    ts.forEachChild(node, visit);
  }

  visit(sourceFile);
  return metrics;
}

// Week 17 files to check
const week17Files = [
  'src/components/three/Loop1FlowerGarden3D.tsx',
  'src/components/three/Loop2BeehiveVillage3D.tsx',
  'src/components/three/Loop3HoneycombLayers3D.tsx',
  'src/components/three/models/Bee3D.tsx',
  'src/components/three/models/Flower3D.tsx',
  'src/components/three/models/HoneycombCell3D.tsx',
  'src/lib/three/animations/BeeFlightPath.ts',
  'src/components/patterns/HoneycombPattern.tsx',
  'src/components/patterns/WingShimmer.tsx',
  'src/components/patterns/PollenTexture.tsx',
  'src/components/three/LoopNavigation.tsx',
];

let totalFunctions = 0;
let compliantFunctions = 0;
const violations: FunctionMetrics[] = [];
const fileMetrics: Map<string, { total: number; compliant: number }> = new Map();

console.log('\n🔍 NASA Rule 10 Compliance Check');
console.log('━'.repeat(70));
console.log('Target: ≤60 lines per function, ≥95% compliance\n');

week17Files.forEach(file => {
  const fullPath = path.join(process.cwd(), file);

  if (!fs.existsSync(fullPath)) {
    console.log(`⚠️  File not found: ${file}`);
    return;
  }

  const metrics = checkFile(fullPath);
  const fileCompliant = metrics.filter(m => m.compliant).length;

  fileMetrics.set(file, {
    total: metrics.length,
    compliant: fileCompliant,
  });

  metrics.forEach(m => {
    totalFunctions++;
    if (m.compliant) {
      compliantFunctions++;
    } else {
      violations.push(m);
    }
  });
});

const complianceRate = totalFunctions > 0 ? (compliantFunctions / totalFunctions) * 100 : 0;
const passed = complianceRate >= 95;

console.log('📊 Per-File Summary:');
console.log('━'.repeat(70));
fileMetrics.forEach((stats, file) => {
  const rate = stats.total > 0 ? (stats.compliant / stats.total) * 100 : 0;
  const status = rate >= 95 ? '✅' : rate >= 90 ? '🔶' : '❌';
  console.log(`${status} ${path.basename(file).padEnd(35)} ${stats.compliant}/${stats.total} (${rate.toFixed(1)}%)`);
});

console.log('\n📈 Overall Compliance:');
console.log('━'.repeat(70));
console.log(`Total Functions Checked: ${totalFunctions}`);
console.log(`Compliant (≤60 LOC):     ${compliantFunctions} (${complianceRate.toFixed(1)}%)`);
console.log(`Violations (>60 LOC):    ${violations.length}`);
console.log(`Target:                  ≥95%`);
console.log(`Status:                  ${passed ? '✅ PASS' : '❌ FAIL'}`);

if (violations.length > 0) {
  console.log('\n⚠️  Violations (Functions >60 LOC):');
  console.log('━'.repeat(70));
  violations.sort((a, b) => b.lineCount - a.lineCount);  // Sort by line count DESC
  violations.forEach(v => {
    const severity = v.lineCount > 80 ? '❌' : '⚠️';
    console.log(`${severity} ${v.file}:${v.startLine}-${v.endLine}`);
    console.log(`   Function: ${v.name}`);
    console.log(`   Lines: ${v.lineCount} (${v.lineCount - 60} over limit)`);
    console.log('');
  });
}

console.log('\n💡 Recommendations:');
console.log('━'.repeat(70));
if (passed) {
  console.log('✅ Excellent! Week 17 code meets NASA Rule 10 compliance.');
  console.log('   Continue maintaining function length discipline.');
} else if (complianceRate >= 90) {
  console.log('🔶 Close to target. Consider refactoring the largest violations.');
  console.log('   Focus on functions >80 LOC first.');
} else {
  console.log('❌ Below target. Refactoring needed for production readiness.');
  console.log('   Break down long functions into smaller, focused units.');
}

console.log('\n━'.repeat(70));
console.log(`Generated: ${new Date().toISOString()}`);
console.log('Report: Week 17 NASA Rule 10 Compliance\n');

// Exit with appropriate code
process.exit(passed ? 0 : 1);
