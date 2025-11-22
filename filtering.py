def filter_data(data, column, value, op="=="):
    # case insensitive headers from keys
    headers = {h.lower().strip(): h for h in data[0].keys()}

    # check if requested column exists
    col_key = column.lower().strip()
    if col_key not in headers:
        raise KeyError(f"Invalid column '{column}' for this dataset. Resetting to none.")

    actual_col = headers[col_key]

    filtered = []
    for row in data:
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
            filtered.append(row)

    return filtered