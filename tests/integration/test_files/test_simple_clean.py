"""Simple clean Python file for integration testing.

Expected Results:
- Radon CC: 1-2 (rank A)
- Radon MI: 85-100 (rank A)
- Pylint: No violations or low severity only
"""


def add(a: int, b: int) -> int:
    """Add two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b

    Raises:
        AssertionError: If inputs are not integers
    """
    assert isinstance(a, int), "a must be int"
    assert isinstance(b, int), "b must be int"
    return a + b


def multiply(a: int, b: int) -> int:
    """Multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Product of a and b

    Raises:
        AssertionError: If inputs are not integers
    """
    assert isinstance(a, int), "a must be int"
    assert isinstance(b, int), "b must be int"
    return a * b
