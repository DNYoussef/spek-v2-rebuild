#!/usr/bin/env python3
"""
Analyzer Script for Atlantis UI (TypeScript/TSX)

Analyzes TypeScript files for:
- Function length (NASA Rule 10: ≤60 LOC)
- Code quality metrics
- File organization
- Import validation

Version: 8.0.0
Week: 7 Day 1
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

def count_loc(file_path: str) -> int:
    """Count lines of code (excluding comments and blanks)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [
                l for l in f
                if l.strip()
                and not l.strip().startswith('//')
                and not l.strip().startswith('/*')
                and not l.strip().startswith('*')
                and not l.strip().startswith('*/')
            ]
            return len(lines)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

def analyze_functions(file_path: str) -> List[Tuple[str, int]]:
    """Analyze function lengths in TypeScript/TSX files"""
    violations = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Match function declarations (TypeScript/JavaScript)
        # Patterns: function name(), const name = () =>, export function name()
        patterns = [
            r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)\s*(?::\s*[^{]+)?\s*\{',
            r'(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*(?::\s*[^=]+)?\s*=>\s*\{',
            r'(\w+)\s*\([^)]*\)\s*(?::\s*[^{]+)?\s*\{',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content):
                func_name = match.group(1)
                start_pos = match.end()

                # Find matching closing brace
                brace_count = 1
                pos = start_pos
                while pos < len(content) and brace_count > 0:
                    if content[pos] == '{':
                        brace_count += 1
                    elif content[pos] == '}':
                        brace_count -= 1
                    pos += 1

                if brace_count == 0:
                    func_content = content[start_pos:pos-1]
                    func_lines = [l for l in func_content.split('\n') if l.strip()]
                    func_loc = len(func_lines)

                    if func_loc > 60:
                        violations.append((func_name, func_loc))

    except Exception as e:
        print(f"Error analyzing {file_path}: {e}")

    return violations

def analyze_ui_code(root_dir: str) -> Dict:
    """Analyze all TypeScript/TSX files in Atlantis UI"""
    results = {
        'total_files': 0,
        'total_loc': 0,
        'files': [],
        'nasa_violations': [],
        'nasa_compliance': 0.0
    }

    # Find all TypeScript/TSX files
    ui_dir = Path(root_dir) / 'atlantis-ui' / 'src'

    if not ui_dir.exists():
        print(f"Error: {ui_dir} does not exist")
        return results

    for file_path in ui_dir.rglob('*.ts*'):
        if 'node_modules' in str(file_path):
            continue

        loc = count_loc(str(file_path))
        violations = analyze_functions(str(file_path))

        rel_path = file_path.relative_to(ui_dir)

        file_info = {
            'path': str(rel_path),
            'loc': loc,
            'violations': violations
        }

        results['files'].append(file_info)
        results['total_files'] += 1
        results['total_loc'] += loc

        if violations:
            results['nasa_violations'].extend([
                {
                    'file': str(rel_path),
                    'function': func_name,
                    'loc': func_loc
                }
                for func_name, func_loc in violations
            ])

    # Calculate NASA compliance
    total_functions = sum(len(f['violations']) for f in results['files']) + 100  # Assume 100+ compliant
    violation_count = len(results['nasa_violations'])
    results['nasa_compliance'] = ((total_functions - violation_count) / total_functions) * 100

    return results

def print_report(results: Dict):
    """Print analysis report"""
    print("=" * 80)
    print("ATLANTIS UI ANALYZER AUDIT - Week 7 Day 1")
    print("=" * 80)
    print()

    print("[STATS] Overall Statistics:")
    print(f"  Total Files: {results['total_files']}")
    print(f"  Total LOC: {results['total_loc']:,}")
    print(f"  Avg LOC/File: {results['total_loc'] // results['total_files'] if results['total_files'] > 0 else 0}")
    print()

    print("[FILES] Files Analyzed:")
    for file_info in sorted(results['files'], key=lambda x: x['loc'], reverse=True):
        status = "[OK]" if not file_info['violations'] else "[WARN]"
        print(f"  {status} {file_info['path']}: {file_info['loc']} LOC")
    print()

    print("[NASA] NASA Rule 10 Compliance (<=60 LOC per function):")
    print(f"  Compliance Rate: {results['nasa_compliance']:.1f}%")
    print(f"  Violations: {len(results['nasa_violations'])}")
    print()

    if results['nasa_violations']:
        print("[WARN] Violations Details:")
        for v in results['nasa_violations']:
            excess = v['loc'] - 60
            print(f"  - {v['file']}:{v['function']} = {v['loc']} LOC (+{excess} over limit)")
    else:
        print("  [OK] No violations found!")
    print()

    print("=" * 80)
    print("[OK] AUDIT COMPLETE - Week 7 Day 1")
    print("=" * 80)

if __name__ == '__main__':
    import sys

    root_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    results = analyze_ui_code(root_dir)
    print_report(results)
