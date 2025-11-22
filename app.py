# app.py
from flask import Flask, render_template, request
from parse import csvParser
from table import DataTable
from filtering import filter_data
from innerJoin import inner_join
from group_aggregation import group_and_aggregate

app = Flask(__name__)

# ---------- Load datasets on startup ----------

tables = {}

def load_tables():
    # Ratings dataset (your restaurant ratings CSV)
    ratings_parser = csvParser("Ratings_Type_Link.csv")
    ratings_table = DataTable.from_parser(ratings_parser)
    tables["ratings"] = ratings_table

    # Healthgrade dataset
    health_parser = csvParser("Healthgrade.csv")
    health_table = DataTable.from_parser(health_parser)
    tables["healthgrade"] = health_table

    combined_parser = inner_join(ratings_parser, "Restaurant Name", health_parser, "Facility Name")
    combined_table = DataTable.from_parser(combined_parser)
    tables["combined"] = combined_table
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

        # Apply filter if provided
        if filter_column and filter_value:
            try:
                working_rows = filter_data(table.rows, filter_column, filter_value, filter_operator)
                # working = DataTable(working_rows, headers=table.headers)  # wrap back into your Table class if needed
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
    app.run(debug=True)
