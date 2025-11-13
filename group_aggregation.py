from collections import defaultdict

def group_and_aggregate(data, group_by, agg_column, agg_func="count"):
    # agg_func: one of ["count", "sum", "avg", "min", "max"]

    # Normalize headers
    headers = {h.lower().strip(): h for h in data[0].keys()}
    group_key = group_by.lower().strip()
    agg_key = agg_column.lower().strip()

    if group_key not in headers or agg_key not in headers:
        raise KeyError(f"Invalid column. Available: {list(data[0].keys())}")

    group_col = headers[group_key]
    agg_col = headers[agg_key]

    grouped = defaultdict(list)

    for row in data:
        grouped[row[group_col]].append(row[agg_col])

    results = {}
    for g, values in grouped.items():
        # Convert to numeric if possible
        try:
            values = [float(v) for v in values]
        except ValueError:
            raise ValueError(f"Column '{agg_col}' must contain numeric values")

        if agg_func == "count":
            results[g] = len(values)
        elif agg_func == "sum":
            results[g] = sum(values)
        elif agg_func == "avg":
            results[g] = sum(values) / len(values)
        elif agg_func == "min":
            results[g] = min(values)
        elif agg_func == "max":
            results[g] = max(values)
        else:
            raise ValueError(f"Unsupported aggregation '{agg_func}'")

    return results