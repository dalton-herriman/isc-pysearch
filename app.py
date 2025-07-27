from flask import Flask, render_template, jsonify
app = Flask(__name__)


# Sample data
users = [
    {"name": "John Doe", "email": "john@example.com", "role": "Admin"},
    {"name": "Jane Smith", "email": "jane@example.com", "role": "User"},
    {"name": "Sam Wilson", "email": "sam@example.com", "role": "Manager"},
]


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    # Render only the <tr> rows for HTMX to inject
    return render_template("table_rows.html", users=users)

if __name__ == "__main__":
    app.run(debug=True)