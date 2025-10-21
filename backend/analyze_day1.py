#!/usr/bin/env python3
"""
Week 8 Day 1 Backend Analyzer
Checks NASA Rule 10 compliance and code quality for backend tRPC router
"""

import ast
import os
from pathlib import Path
from typing import List, Dict

def analyze_file(file_path: str) -> Dict:
    """Analyze a single TypeScript/JavaScript file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = [l for l in content.split('\n') if l.strip() and not l.strip().startswith('//')]
    loc = len(lines)

    # Count functions (simple heuristic for TypeScript)
    functions = []
    in_function = False
    func_start = 0
    func_name = ""
    brace_count = 0

    for i, line in enumerate(content.split('\n'), 1):
        # Detect function declarations
        if ('function ' in line or '=>' in line or 'async' in line) and '{' in line:
            if not in_function:
                in_function = True
                func_start = i
                # Extract function name (simple)
                if 'function ' in line:
                    func_name = line.split('function ')[1].split('(')[0].strip()
                elif 'const ' in line or 'export const ' in line:
                    func_name = line.split('const ')[1].split('=')[0].strip() if 'const ' in line else line.split('export const ')[1].split('=')[0].strip()
                else:
                    func_name = f"anonymous_{i}"

        # Count braces
        if in_function:
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0 and func_start != i:
                # Function ended
                func_length = i - func_start + 1
                functions.append({
                    'name': func_name,
                    'start': func_start,
                    'end': i,
                    'length': func_length,
                    'compliant': func_length <= 60
                })
                in_function = False
                func_name = ""
                brace_count = 0

    # NASA compliance check
    compliant_funcs = [f for f in functions if f['compliant']]
    compliance_rate = (len(compliant_funcs) / len(functions) * 100) if functions else 100

    return {
        'file': file_path,
        'loc': loc,
        'functions': len(functions),
        'compliant_functions': len(compliant_funcs),
        'compliance_rate': compliance_rate,
        'violations': [f for f in functions if not f['compliant']]
    }

def main():
    """Analyze all backend TypeScript files"""
    backend_dir = Path(__file__).parent / 'src'
    results = []

    for file_path in backend_dir.rglob('*.ts'):
        result = analyze_file(str(file_path))
        results.append(result)

    # Summary
    total_loc = sum(r['loc'] for r in results)
    total_funcs = sum(r['functions'] for r in results)
    total_compliant = sum(r['compliant_functions'] for r in results)
    overall_compliance = (total_compliant / total_funcs * 100) if total_funcs else 100

    print("=" * 80)
    print("WEEK 8 DAY 1 BACKEND ANALYSIS")
    print("=" * 80)
    print(f"\nTotal Files: {len(results)}")
    print(f"Total LOC: {total_loc}")
    print(f"Total Functions: {total_funcs}")
    print(f"Compliant Functions: {total_compliant}")
    print(f"NASA Compliance Rate: {overall_compliance:.1f}%")
    print()

    # File-by-file breakdown
    print("\nPER-FILE BREAKDOWN:")
    print("-" * 80)
    for r in results:
        file_name = Path(r['file']).name
        status = "✅" if r['compliance_rate'] >= 92 else "⚠️"
        print(f"{status} {file_name:30} | {r['loc']:4} LOC | {r['functions']:2} funcs | {r['compliance_rate']:5.1f}% compliant")

    # Violations
    violations = [v for r in results for v in r['violations']]
    if violations:
        print(f"\n\nNASA VIOLATIONS ({len(violations)}):")
        print("-" * 80)
        for v in violations:
            print(f"  • {v['name']} ({v['length']} LOC) - Exceeds 60 line limit by {v['length'] - 60} lines")
    else:
        print("\n✅ NO NASA VIOLATIONS!")

    print("\n" + "=" * 80)
    print(f"OVERALL RESULT: {'✅ PASS' if overall_compliance >= 92 else '⚠️ NEEDS IMPROVEMENT'}")
    print(f"Target: ≥92% compliance | Actual: {overall_compliance:.1f}%")
    print("=" * 80)

if __name__ == '__main__':
    main()
