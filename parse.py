import csv

class csvParser:
    def __init__(self, filename):
        self.filename = filename
        self.data = []
        self.headers = []
        self._parse()

    def _parse(self):
        with open(self.filename, newline='', encoding="utf-8-sig") as f: # need this encoding, otherwise will also have BOM Byte Order Mark in dict keys
            reader = csv.reader(f)
            self.headers = next(reader)  # first row as header
            for row in reader:
                self.data.append(dict(zip(self.headers, row)))

    def head(self, n=5):
        # default of 5 but can input any n
        return self.data[:n]

    def drop_dup(self):
        seen = set()
        unique_data = []
        for row in self.data:
            row_tuple = tuple(row.items())
            if row_tuple not in seen:
                seen.add(row_tuple)
                unique_data.append(row)
        self.data = unique_data

    def add_row(self, row_dict):
        # Add a new row with dict with keys matching headers
        if not set(row_dict.keys()).issubset(set(self.headers)):
            raise ValueError("Data Dict Row keys must match CSV headers")
        self.data.append(row_dict)

    def drop_row(self, index):
        # Drop a row by index
        if 0 <= index < len(self.data):
            self.data.pop(index)
        else:
            raise IndexError("Data Row index out of range")

    def to_csv(self, out_filename):
        # Save cleaned or editted data back to CSV
        with open(out_filename, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()
            writer.writerows(self.data)


