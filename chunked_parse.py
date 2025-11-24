import csv

class ChunkedCSVParser:
    """
    A CSV parser that reads files in chunks to handle large datasets
    that don't fit in memory.
    """
    def __init__(self, filename, chunk_size=10000):
        self.filename = filename
        self.chunk_size = chunk_size
        self.headers = []
        self._read_headers()
    
    def _read_headers(self):
        """Read headers from the CSV file."""
        try:
            with open(self.filename, newline='', encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                self.headers = next(reader)
        except UnicodeDecodeError:
            with open(self.filename, newline='', encoding="latin-1") as f:
                reader = csv.reader(f)
                self.headers = next(reader)
    
    def iter_chunks(self):
        """
        Generator that yields chunks of data as lists of dictionaries.
        Each chunk contains up to chunk_size rows.
        """
        try:
            with open(self.filename, newline='', encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                chunk = []
                for row in reader:
                    chunk.append(row)
                    if len(chunk) >= self.chunk_size:
                        yield chunk
                        chunk = []
                # Yield remaining rows
                if chunk:
                    yield chunk
        except UnicodeDecodeError:
            with open(self.filename, newline='', encoding="latin-1") as f:
                reader = csv.DictReader(f)
                chunk = []
                for row in reader:
                    chunk.append(row)
                    if len(chunk) >= self.chunk_size:
                        yield chunk
                        chunk = []
                # Yield remaining rows
                if chunk:
                    yield chunk
    
    def iter_rows(self):
        """
        Generator that yields individual rows as dictionaries.
        """
        try:
            with open(self.filename, newline='', encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield row
        except UnicodeDecodeError:
            with open(self.filename, newline='', encoding="latin-1") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield row

