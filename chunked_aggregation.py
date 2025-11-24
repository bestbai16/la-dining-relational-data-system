from collections import defaultdict

def group_and_aggregate_chunked(data_iter, group_by, agg_column, agg_func="count", headers=None):
    """
    Group and aggregate data in chunks. data_iter should be an iterator over chunks.
    Returns aggregated results dictionary.
    """
    # Get headers from first chunk if not provided
    if headers is None:
        first_chunk = next(data_iter, [])
        if not first_chunk:
            return {}
        headers_map = {h.lower().strip(): h for h in first_chunk[0].keys()}
        data_iter = iter([first_chunk] + list(data_iter))
    else:
        headers_map = {h.lower().strip(): h for h in headers}
    
    group_key = group_by.lower().strip()
    agg_key = agg_column.lower().strip()
    
    if group_key not in headers_map or agg_key not in headers_map:
        raise KeyError(f"Invalid column. Available: {list(headers_map.keys())}")
    
    group_col = headers_map[group_key]
    agg_col = headers_map[agg_key]
    
    # Accumulate values across all chunks
    grouped = defaultdict(list)
    
    for chunk in data_iter:
        for row in chunk:
            grouped[row[group_col]].append(row[agg_col])
    
    # Compute aggregations
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

