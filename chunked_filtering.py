def filter_data_chunked(data_iter, column, value, op="==", headers=None):
    """
    Filter data in chunks. data_iter should be an iterator over chunks (lists of dicts).
    Returns a generator that yields filtered rows.
    """
    # Get headers from first chunk if not provided
    if headers is None:
        first_chunk = next(data_iter, [])
        if not first_chunk:
            return
        headers_map = {h.lower().strip(): h for h in first_chunk[0].keys()}
        data_iter = iter([first_chunk] + list(data_iter))
    else:
        headers_map = {h.lower().strip(): h for h in headers}
    
    # Check if requested column exists
    col_key = column.lower().strip()
    if col_key not in headers_map:
        raise KeyError(f"Invalid column '{column}' for this dataset.")
    
    actual_col = headers_map[col_key]
    
    for chunk in data_iter:
        for row in chunk:
            cell_value = row.get(actual_col, "").strip()
            
            # Handle numeric Rating column
            if actual_col.lower() == "rating" or actual_col.lower() == "score":
                try:
                    num = float(cell_value)
                    target = float(value)
                except ValueError:
                    raise ValueError("Rating values must be numeric")
                
                if op == "==":
                    condition = num == target
                elif op == ">":
                    condition = num > target
                elif op == "<":
                    condition = num < target
                elif op == ">=":
                    condition = num >= target
                elif op == "<=":
                    condition = num <= target
                else:
                    raise ValueError(f"Unsupported operator '{op}'")
            else:
                # Case-insensitive string comparison
                condition = cell_value.lower() == str(value).lower()
            
            if condition:
                yield row

