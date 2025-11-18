# app.py
from flask import Flask, render_template, request
from parse import csvParser
from table import DataTable

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

load_tables()

# ---------- Routes ----------

@app.route("/", methods=["GET", "POST"])
def index():
    dataset_name = request.form.get("dataset") or "ratings"
    table = tables.get(dataset_name)

    headers = table.headers if table else []

    # Defaults
    selected_columns = []
    result_table = None
    filter_column = ""
    filter_value = ""

    if request.method == "POST":
        # Projection columns
        selected_columns = request.form.getlist("columns")

        # Simple filter inputs
        filter_column = request.form.get("filter_column", "")
        filter_value = request.form.get("filter_value", "")

        # Start from the chosen dataset
        working = table

        # Apply filter if provided
        if filter_column and filter_value:
            try:
                working = working.filter_equals(filter_column, filter_value)
            except ValueError as e:
                # Show error in template as flash-like message if needed
                return render_template(
                    "index.html",
                    datasets=list(tables.keys()),
                    current_dataset=dataset_name,
                    headers=headers,
                    selected_columns=selected_columns,
                    result_table=None,
                    error=str(e),
                    filter_column=filter_column,
                    filter_value=filter_value,
                )

        # Apply projection if columns selected, otherwise just show head()
        if selected_columns:
            try:
                working = working.project(selected_columns)
            except ValueError as e:
                return render_template(
                    "index.html",
                    datasets=list(tables.keys()),
                    current_dataset=dataset_name,
                    headers=headers,
                    selected_columns=selected_columns,
                    result_table=None,
                    error=str(e),
                    filter_column=filter_column,
                    filter_value=filter_value,
                )

        # Limit rows shown for UI
        result_table = {
            "headers": working.headers,
            "rows": working.head(50),  # show up to 50 rows
        }

    return render_template(
        "index.html",
        datasets=list(tables.keys()),
        current_dataset=dataset_name,
        headers=headers,
        selected_columns=selected_columns,
        result_table=result_table,
        error=None,
        filter_column=filter_column,
        filter_value=filter_value,
    )

if __name__ == "__main__":
    app.run(debug=True)
