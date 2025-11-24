# app.py
import os
from flask import Flask, render_template, request
from parse import csvParser
from table import DataTable
from filtering import filter_data
from innerJoin import inner_join
from group_aggregation import group_and_aggregate
from chunked_parse import ChunkedCSVParser
from chunked_table import ChunkedDataTable
from chunked_filtering import filter_data_chunked
from chunked_aggregation import group_and_aggregate_chunked

app = Flask(__name__)

# Configuration
# Memory threshold in MB - files larger than this will use chunked processing
MEMORY_THRESHOLD_MB = 50
CHUNK_SIZE = 10000  

# Load datasets on startup

tables = {}
table_parsers = {}  # Store parsers for chunked tables

def get_file_size_mb(filename):
    """Get file size in MB."""
    if not os.path.exists(filename):
        return 0
    return os.path.getsize(filename) / (1024 * 1024)

def load_tables():
    # Ratings dataset (your restaurant ratings CSV)
    ratings_file = "Ratings_Type_Link.csv"
    if get_file_size_mb(ratings_file) > MEMORY_THRESHOLD_MB:
        # Use chunked processing for large files
        ratings_parser = ChunkedCSVParser(ratings_file, chunk_size=CHUNK_SIZE)
        ratings_table = ChunkedDataTable.from_parser(ratings_parser, chunk_size=CHUNK_SIZE)
        tables["ratings"] = ratings_table
        table_parsers["ratings"] = ratings_parser
    else:
        # Use regular processing for small files
        ratings_parser = csvParser(ratings_file)
        ratings_table = DataTable.from_parser(ratings_parser)
        tables["ratings"] = ratings_table
        table_parsers["ratings"] = ratings_parser

    # Healthgrade dataset
    health_file = "Healthgrade.csv"
    if get_file_size_mb(health_file) > MEMORY_THRESHOLD_MB:
        # Use chunked processing for large files
        health_parser = ChunkedCSVParser(health_file, chunk_size=CHUNK_SIZE)
        health_table = ChunkedDataTable.from_parser(health_parser, chunk_size=CHUNK_SIZE)
        tables["healthgrade"] = health_table
        table_parsers["healthgrade"] = health_parser
    else:
        # Use regular processing for small files
        health_parser = csvParser(health_file)
        health_table = DataTable.from_parser(health_parser)
        tables["healthgrade"] = health_table
        table_parsers["healthgrade"] = health_parser

    # Combined dataset - for now, we'll use regular join (can be optimized later)
    # Note: inner_join currently requires full data in memory
    # For very large datasets, you'd need a chunked join implementation
    try:
        if isinstance(ratings_parser, ChunkedCSVParser) or isinstance(health_parser, ChunkedCSVParser):
            # For chunked parsers, we need to load data for join (or implement chunked join)
            # For now, we'll skip the combined table if both are chunked
            # In production, you'd implement a chunked join
            print("Warning: Combined table not created for chunked datasets (requires chunked join implementation)")
        else:
            combined_parser = inner_join(ratings_parser, "Restaurant Name", health_parser, "Facility Name")
            combined_table = DataTable.from_parser(combined_parser)
            tables["combined"] = combined_table
            table_parsers["combined"] = combined_parser
    except Exception as e:
        print(f"Warning: Could not create combined table: {e}")

load_tables()

# ---------- Routes ----------

@app.route("/", methods=["GET", "POST"])
def index():
    #dataset_name = request.form.get("dataset") or "ratings"
    #table = tables.get(dataset_name)
    #headers = table.headers if table else []

    dataset_name = request.form.get("dataset", "ratings")
    table = tables[dataset_name]
    headers = table.headers

    filter_column = request.form.get("filter_column", "")
    if filter_column not in headers:
        filter_column = ""  # reset if invalid

    # Defaults
    selected_columns = []
    result_table = None
    filter_column = ""
    filter_value = ""
    filter_operator = "=="
    group_by_column = ""
    aggregate_column = ""
    aggregate_function = "count"

    if request.method == "POST":
        # Projection columns
        selected_columns = request.form.getlist("columns")
        selected_columns = [c for c in selected_columns if c in headers]

        # Simple filter inputs
        filter_column = request.form.get("filter_column", "")
        filter_value = request.form.get("filter_value", "")
        filter_operator = request.form.get("filter_operator", "==")

        # Group by and aggregate inputs
        group_by_column = request.form.get("group_by_column", "")
        aggregate_column = request.form.get("aggregate_column", "")
        aggregate_function = request.form.get("aggregate_function", "count")


        # Start from the chosen dataset
        working = table
        is_chunked = isinstance(table, ChunkedDataTable)

        # Apply filter if provided
        if filter_column and filter_value:
            try:
                if is_chunked:
                    # Use chunked filtering
                    filtered_rows = list(filter_data_chunked(
                        table.iter_chunks(), 
                        filter_column, 
                        filter_value, 
                        filter_operator,
                        headers=table.headers
                    ))
                    # Create a regular DataTable from filtered results (smaller now)
                    from parse import csvParser
                    temp_parser = csvParser.from_data(table.headers, filtered_rows)
                    working = DataTable.from_parser(temp_parser)
                    is_chunked = False  # Now it's a regular table
                else:
                    # Use regular filtering
                    working_rows = filter_data(table.rows, filter_column, filter_value, filter_operator)
                    working = DataTable(table.headers, working_rows)
            except Exception as e:
                return render_template(
                    "index - Copy.html",
                    datasets=list(tables.keys()),
                    current_dataset=dataset_name,
                    headers=headers,
                    selected_columns=selected_columns,
                    result_table=None,
                    error=str(e),
                    filter_column=filter_column,
                    filter_operator=filter_operator,
                    filter_value=filter_value,
                    group_by_column=group_by_column,
                    aggregate_column=aggregate_column,
                    aggregate_function=aggregate_function,
                )

        # Apply group by and aggregate if specified (before projection)
        if group_by_column and aggregate_column:
            try:
                # Validate that columns exist in original table headers (before projection)
                if group_by_column not in headers:
                    raise ValueError(f"Group by column '{group_by_column}' not found in table headers")
                if aggregate_column not in headers:
                    raise ValueError(f"Aggregate column '{aggregate_column}' not found in table headers")
                
                # Use chunked or regular aggregation based on table type
                if is_chunked:
                    aggregated_results = group_and_aggregate_chunked(
                        working.iter_chunks(),
                        group_by_column,
                        aggregate_column,
                        aggregate_function,
                        headers=working.headers
                    )
                else:
                    # Convert DataTable rows to list of dicts for group_and_aggregate
                    data_rows = working.rows
                    aggregated_results = group_and_aggregate(
                        data_rows, 
                        group_by_column, 
                        aggregate_column, 
                        aggregate_function
                    )
                
                # Convert aggregated results dictionary to table format
                agg_headers = [group_by_column, f"{aggregate_function.upper()}({aggregate_column})"]
                agg_rows = [
                    {group_by_column: key, f"{aggregate_function.upper()}({aggregate_column})": value}
                    for key, value in aggregated_results.items()
                ]
                
                # Sort by group_by_column for better display
                agg_rows.sort(key=lambda x: str(x[group_by_column]))
                
                # Create a DataTable from aggregated results
                working = DataTable(agg_headers, agg_rows)
            except Exception as e:
                return render_template(
                    "index - Copy.html",
                    datasets=list(tables.keys()),
                    current_dataset=dataset_name,
                    headers=headers,
                    selected_columns=selected_columns,
                    result_table=None,
                    error=str(e),
                    filter_column=filter_column,
                    filter_operator=filter_operator,
                    filter_value=filter_value,
                    group_by_column=group_by_column,
                    aggregate_column=aggregate_column,
                    aggregate_function=aggregate_function,
                )

        # Apply projection if columns selected, otherwise just show head()
        if selected_columns:
            try:
                if is_chunked:
                    working = working.project(selected_columns)
                    # After projection, convert to regular table if it's small enough
                    if isinstance(working, ChunkedDataTable):
                        all_rows = working.get_all_rows()
                        if len(all_rows) < 100000:  # If result is small, convert to regular table
                            from parse import csvParser
                            temp_parser = csvParser.from_data(working.headers, all_rows)
                            working = DataTable.from_parser(temp_parser)
                            is_chunked = False
                else:
                    working = working.project(selected_columns)
            except Exception as e:
                return render_template(
                    "index - Copy.html",
                    datasets=list(tables.keys()),
                    current_dataset=dataset_name,
                    headers=headers,
                    selected_columns=selected_columns,
                    result_table=None,
                    error=str(e),
                    filter_column=filter_column,
                    filter_operator=filter_operator,
                    filter_value=filter_value,
                    group_by_column=group_by_column,
                    aggregate_column=aggregate_column,
                    aggregate_function=aggregate_function,
                )

        # Limit rows shown for UI
        if is_chunked:
            # For chunked tables, just get the head
            result_table = {
                "headers": working.headers,
                "rows": working.head(50),  # show up to 50 rows
            }
        else:
            # For regular tables
            result_table = {
                "headers": working.headers,
                "rows": working.head(50),  # show up to 50 rows
            }

    return render_template(
        "index - Copy.html",
        datasets=list(tables.keys()),
        current_dataset=dataset_name,
        headers=headers,
        selected_columns=selected_columns,
        result_table=result_table,
        error=None,
        filter_column=filter_column,
        filter_operator=filter_operator,
        filter_value=filter_value,
        group_by_column=group_by_column,
        aggregate_column=aggregate_column,
        aggregate_function=aggregate_function,
    )

if __name__ == "__main__":
     app.run(
        debug=True,
        host="127.0.0.1",
        port=5001,  # <-- use a different port to avoid conflicts
    )
