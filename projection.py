from parse import csvParser


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
        # 1. Validate column names
        missing = [c for c in columns if c not in self.headers]
        if missing:
            raise ValueError(f"Columns not found in table headers: {missing}")

        # 2. Build projected rows
        projected_rows = []
        for row in self.rows:
            projected_row = {col: row[col] for col in columns}
            projected_rows.append(projected_row)

        # 3. Return a new DataTable
        return DataTable(columns, projected_rows)


if __name__ == "__main__":
    # ---------- Ratings_Type_Link / restaurant dataset ----------
    restaurants_parser = csvParser("Ratings_Type_Link.csv")
    restaurants_table = DataTable.from_parser(restaurants_parser)

    print("Restaurant headers:", restaurants_table.headers)

    projected_restaurants = restaurants_table.project([
        "Restaurant Name",
        "Cuisine Type",
        "Neighborhood",
        "Rating",
    ])

    print("\nFirst 3 projected restaurant rows:")
    for row in projected_restaurants.head(3):
        print(row)

    # ---------- Healthgrade dataset ----------
    health_parser = csvParser("Healthgrade.csv", encoding="latin-1")
    health_table = DataTable.from_parser(health_parser)

    print("\nHealthgrade headers:", health_table.headers)

    projected_health = health_table.project([
        "FACILITY NAME",
        "OWNER NAME",
        "FACILITY ZIP",
        "SCORE",
        "GRADE",
    ])

    print("\nFirst 5 projected Healthgrade rows:")
    for row in projected_health.head(5):
        print(row)
