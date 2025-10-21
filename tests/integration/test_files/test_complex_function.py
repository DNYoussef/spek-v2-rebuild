"""Complex Python file for integration testing.

Expected Results:
- Radon CC: 15-20 (rank C/D)
- Radon MI: 40-60 (rank B/C)
- Pylint: Multiple refactoring suggestions
"""


def complex_logic(data):
    """Process data with complex conditional logic.

    Expected CC: 15-20 (high complexity)
    """
    # High cyclomatic complexity (15+ paths)
    if data is None:
        return None

    if len(data) == 0:
        return []

    if not isinstance(data, list):
        data = [data]

    results = []
    for item in data:
        if isinstance(item, str):
            if len(item) > 10:
                results.append(item.upper())
            else:
                results.append(item.lower())
        elif isinstance(item, int):
            if item > 100:
                results.append(item * 2)
            elif item > 50:
                results.append(item * 1.5)
            elif item > 25:
                results.append(item * 1.2)
            else:
                results.append(item)
        elif isinstance(item, dict):
            if 'value' in item:
                if item['value'] > 0:
                    results.append(item['value'])
                else:
                    results.append(0)
            else:
                results.append(None)
        elif isinstance(item, float):
            if item > 100.0:
                results.append(int(item * 2))
            elif item > 50.0:
                results.append(int(item * 1.5))
            else:
                results.append(int(item))

    return results
