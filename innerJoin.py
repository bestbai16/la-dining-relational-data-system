from parse import csvParser

def inner_join(parser1, col1, parser2, col2):
    """
    Perform an inner join between two csvParser objects on the specified columns.
    Returns a new csvParser instance.
    """
    # Build lookup for parser2
    lookup = {}
    for row in parser2.data:
        key = row.get(col2)
        if key is not None:
            lookup.setdefault(key, []).append(row)

    joined_data = []
    joined_headers = parser1.headers + [h for h in parser2.headers if h != col2]

    for row1 in parser1.data:
        key = row1.get(col1)
        if key in lookup:
            for row2 in lookup[key]:
                merged = dict(row1)
                for h, v in row2.items():
                    if h != col2:
                        merged[h] = v
                joined_data.append(merged)

    return csvParser.from_data(joined_headers, joined_data)
