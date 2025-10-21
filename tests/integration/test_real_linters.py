"""
Integration tests for real linter executables.

This tests the Radon and Pylint bridges with actual executables (not mocks).
"""

from pathlib import Path
from analyzer.linters.radon_bridge import RadonBridge
from analyzer.linters.pylint_bridge import PylintBridge
from analyzer.linters import linter_registry


def test_radon_simple_file():
    """Test Radon bridge with simple clean file."""
    bridge = RadonBridge()
    result = bridge.run(Path('tests/integration/test_files/test_simple_clean.py'))

    print("=== Radon: Simple Clean File ===")
    print(f"Success: {result['success']}")
    print(f"Violations: {len(result['violations'])}")
    print(f"Metrics: {result['metrics']}")
    print(f"Expected: 0 violations (CC=3, rank A)")
    print()


def test_radon_complex_file():
    """Test Radon bridge with complex file."""
    bridge = RadonBridge()
    result = bridge.run(Path('tests/integration/test_files/test_complex_function.py'))

    print("=== Radon: Complex Function File ===")
    print(f"Success: {result['success']}")
    print(f"Violations: {len(result['violations'])}")
    print(f"Metrics: {result['metrics']}")
    if result['violations']:
        for v in result['violations'][:2]:
            print(f"  - {v.severity}: {v.description}")
    print(f"Expected: 1 violation (CC=17, rank C -> medium severity)")
    print()


def test_radon_god_function():
    """Test Radon bridge with god function."""
    bridge = RadonBridge()
    result = bridge.run(Path('tests/integration/test_files/test_god_function.py'))

    print("=== Radon: God Function File ===")
    print(f"Success: {result['success']}")
    print(f"Violations: {len(result['violations'])}")
    print(f"Metrics: {result['metrics']}")
    if result['violations']:
        for v in result['violations']:
            print(f"  - {v.severity}: {v.description}")
    print(f"Expected: 1 violation (CC=37, rank E -> critical severity)")
    print()


def test_pylint_simple_file():
    """Test Pylint bridge with simple file."""
    bridge = PylintBridge()
    result = bridge.run(Path('tests/integration/test_files/test_simple_clean.py'))

    print("=== Pylint: Simple Clean File ===")
    print(f"Success: {result['success']}")
    print(f"Violations: {len(result['violations'])}")
    if result['violations']:
        for v in result['violations'][:5]:
            print(f"  - {v.severity}: {v.description}")
    print(f"Expected: Few convention violations (naming style)")
    print()


def test_pylint_god_function():
    """Test Pylint bridge with god function."""
    bridge = PylintBridge()
    result = bridge.run(Path('tests/integration/test_files/test_god_function.py'))

    print("=== Pylint: God Function File ===")
    print(f"Success: {result['success']}")
    print(f"Violations: {len(result['violations'])}")
    if result['violations']:
        for v in result['violations'][:5]:
            print(f"  - {v.severity}: {v.description}")
    print(f"Expected: Many violations (too many parameters, too complex)")
    print()


def test_registry_integration():
    """Test running both linters via registry."""
    print("=== Registry Integration: All Linters ===")

    # Get available linters
    available = linter_registry.get_available_linters()
    print(f"Available linters: {available}")

    # Run all linters on complex file
    file_path = Path('tests/integration/test_files/test_complex_function.py')
    results = linter_registry.run_all_linters(file_path)

    print(f"\nResults from {len(results)} linters:")
    for linter_name, result in results.items():
        print(f"  - {linter_name}: {len(result.get('violations', []))} violations")

    # Aggregate violations
    violations = linter_registry.aggregate_violations(results)
    print(f"\nTotal aggregated violations: {len(violations)}")
    print()


if __name__ == "__main__":
    # Test availability first
    print("=== Linter Availability ===")
    radon_bridge = RadonBridge()
    pylint_bridge = PylintBridge()
    print(f"Radon available: {radon_bridge.is_available()}")
    print(f"Pylint available: {pylint_bridge.is_available()}")
    print()

    # Run all tests
    test_radon_simple_file()
    test_radon_complex_file()
    test_radon_god_function()
    test_pylint_simple_file()
    test_pylint_god_function()
    test_registry_integration()

    print("=== Integration Testing Complete ===")
