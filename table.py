# table.py

class DataTable:
    def __init__(self, headers, rows):
        self.headers = list(headers)
        self.rows = list(rows)

    @classmethod
    def from_parser(cls, parser_obj):
        return cls(parser_obj.headers, parser_obj.data)

    def head(self, n=5):
        return self.rows[:n]

    def project(self, columns):
        # Validate column names
        missing = [c for c in columns if c not in self.headers]
        if missing:
            raise ValueError(f"Columns not found in table headers: {missing}")

        projected_rows = []
        for row in self.rows:
            projected_row = {col: row[col] for col in columns}
            projected_rows.append(projected_row)

        return DataTable(columns, projected_rows)

    def filter_equals(self, column, value):
        """
        Very simple filter: keep rows where column == value (string compare).
        """
        if column not in self.headers:
            raise ValueError(f"Column '{column}' not in headers")

        filtered_rows = [row for row in self.rows if row.get(column) == value]
        return DataTable(self.headers, filtered_rows)
