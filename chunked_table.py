from chunked_parse import ChunkedCSVParser

class ChunkedDataTable:
    """
    A DataTable that processes data in chunks for memory efficiency.
    Stores only metadata and processes data on-demand.
    """
    def __init__(self, parser, chunk_size=10000):
        """
        Initialize with a ChunkedCSVParser or csvParser.
        If csvParser is provided, it will be used directly (for compatibility).
        """
        self.parser = parser
        self.chunk_size = chunk_size
        self.headers = parser.headers if hasattr(parser, 'headers') else []
        
        # If it's a regular csvParser (not chunked), we can still use it
        if hasattr(parser, 'data') and parser.data is not None:
            self._is_chunked = False
            self._full_data = parser.data
        else:
            self._is_chunked = True
            self._full_data = None
    
    @classmethod
    def from_parser(cls, parser_obj, chunk_size=10000):
        """Create ChunkedDataTable from a parser object."""
        return cls(parser_obj, chunk_size)
    
    def iter_chunks(self):
        """Iterate over data in chunks."""
        if not self._is_chunked:
            # For non-chunked data, yield chunks
            for i in range(0, len(self._full_data), self.chunk_size):
                yield self._full_data[i:i + self.chunk_size]
        else:
            # For chunked parser, use its iterator
            if isinstance(self.parser, ChunkedCSVParser):
                yield from self.parser.iter_chunks()
            else:
                # Fallback: treat as regular data
                if hasattr(self.parser, 'data'):
                    for i in range(0, len(self.parser.data), self.chunk_size):
                        yield self.parser.data[i:i + self.chunk_size]
    
    def iter_rows(self):
        """Iterate over individual rows."""
        if not self._is_chunked:
            yield from self._full_data
        else:
            if isinstance(self.parser, ChunkedCSVParser):
                yield from self.parser.iter_rows()
            else:
                if hasattr(self.parser, 'data'):
                    yield from self.parser.data
    
    def head(self, n=5):
        """Get first n rows (loads only what's needed)."""
        result = []
        count = 0
        for row in self.iter_rows():
            result.append(row)
            count += 1
            if count >= n:
                break
        return result
    
    def project(self, columns):
        """Project columns - processes in chunks."""
        # Validate column names
        missing = [c for c in columns if c not in self.headers]
        if missing:
            raise ValueError(f"Columns not found in table headers: {missing}")
        
        # For chunked processing, we return a generator-based approach
        # But for compatibility, we'll collect results in chunks
        projected_rows = []
        for chunk in self.iter_chunks():
            for row in chunk:
                projected_row = {col: row[col] for col in columns}
                projected_rows.append(projected_row)
        
        # Create a new ChunkedDataTable with projected data
        # For now, we'll create a simple in-memory version
        # In a production system, you might want to write to a temp file
        from parse import csvParser
        temp_parser = csvParser.from_data(columns, projected_rows)
        return ChunkedDataTable(temp_parser, self.chunk_size)
    
    def filter_chunked(self, filter_func):
        """
        Apply a filter function to data in chunks.
        filter_func should be a function that takes a row and returns True/False.
        """
        filtered_rows = []
        for chunk in self.iter_chunks():
            for row in chunk:
                if filter_func(row):
                    filtered_rows.append(row)
        
        # Create a new ChunkedDataTable with filtered data
        from parse import csvParser
        temp_parser = csvParser.from_data(self.headers, filtered_rows)
        return ChunkedDataTable(temp_parser, self.chunk_size)
    
    def get_all_rows(self):
        """
        Get all rows (use with caution for large datasets).
        This loads everything into memory.
        """
        if not self._is_chunked:
            return self._full_data
        
        all_rows = []
        for chunk in self.iter_chunks():
            all_rows.extend(chunk)
        return all_rows
    
    @property
    def rows(self):
        """
        Property to access rows (for compatibility with DataTable).
        WARNING: This loads all rows into memory. Use iter_rows() or iter_chunks() for large datasets.
        """
        return self.get_all_rows()

