import re
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

data_sources = {
    "identities": [
        {"name": "John Doe", "email": "john@example.com", "status": "Active"},
        {"name": "Jane Smith", "email": "jane@example.com", "status": "Inactive"},
        {"name": "Sam Wilson", "email": "sam.wilson@example.com", "status": "Active"},
    ],
    "roles": [
        {"role": "Admin", "description": "Full access"},
        {"role": "User", "description": "Limited access"},
    ],
    "events": [
        {"timestamp": "2025-07-01", "event": "Login", "user": "John Doe"},
        {"timestamp": "2025-07-02", "event": "Password Change", "user": "Jane Smith"},
    ]
}

table_configs = {
    "identities": ["Name", "Email", "Status"],
    "roles": ["Role", "Description"],
    "events": ["Timestamp", "Event", "User"]
}

def parse_query(query):
    parts = re.split(r'\s+(AND|OR)\s+', query, flags=re.IGNORECASE)
    conditions = []
    current_op = "AND"

    for part in parts:
        if part.upper() in ["AND", "OR"]:
            current_op = part.upper()
        else:
            match = re.match(r'(\w+)\s*(=|!=|contains|startswith|endswith|before|after)\s*(.+)', part.strip(), re.I)
            if match:
                field, op, value = match.groups()
                conditions.append((current_op, field.lower(), op.lower(), value.strip()))
    return conditions

def apply_filters(data, query):
    if not query:
        return data

    conditions = parse_query(query)

    def matches(row):
        result = None
        for logical, field, op, value in conditions:
            row_val = str(row.get(field, ""))

            # Wildcards -> convert to regex
            if "*" in value:
                pattern = re.escape(value).replace("\\*", ".*")
                regex = re.compile(f"^{pattern}$", re.I)
                check = bool(regex.match(row_val))
            else:
                check = False
                if op == "=": check = row_val.lower() == value.lower()
                elif op == "!=": check = row_val.lower() != value.lower()
                elif op == "contains": check = value.lower() in row_val.lower()
                elif op == "startswith": check = row_val.lower().startswith(value.lower())
                elif op == "endswith": check = row_val.lower().endswith(value.lower())
                elif op == "before":
                    check = row_val < value if is_date(row_val) and is_date(value) else False
                elif op == "after":
                    check = row_val > value if is_date(row_val) and is_date(value) else False

            if result is None:
                result = check
            elif logical == "AND":
                result = result and check
            elif logical == "OR":
                result = result or check

        return result

    return [row for row in data if matches(row)]

def is_date(val):
    try:
        datetime.fromisoformat(val)
        return True
    except:
        return False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    search_type = request.args.get("type", "identities")
    query = request.args.get("query", "")
    data = data_sources.get(search_type, [])
    filtered = apply_filters(data, query)
    columns = table_configs.get(search_type, [])
    return render_template("table.html", data=filtered, columns=columns)

if __name__ == "__main__":
    app.run(debug=True)