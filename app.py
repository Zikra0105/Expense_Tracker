from flask import Flask, jsonify, render_template, request, redirect
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# ---------- MySQL connection ----------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="expense_db"
)
# Use dictionary=False to get tuples (row[0], …)
cursor = conn.cursor(dictionary=False)

# ---------- Routes ----------
@app.route("/add", methods=["POST"])
def add_expense():
    name = request.form["expense_name"]
    amount = request.form["amount"]
    category = request.form["category"]
    date = request.form["date"] or datetime.today().date()

    cursor.execute(
        "INSERT INTO expenses (expense_name, amount, category, date) "
        "VALUES (%s, %s, %s, %s)",
        (name, amount, category, date)
    )
    conn.commit()
    return redirect("/")


@app.route("/")
def index():
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    rows = cursor.fetchall()

    # Let SQL calculate total
    cursor.execute("SELECT COALESCE(SUM(amount),0) FROM expenses")
    total = cursor.fetchone()[0]

    return render_template("index.html", expenses=rows, total=total)


@app.route("/delete", methods=["POST"])
def delete_expense():
    data = request.get_json(silent=True)  # silent avoids HTML error page
    exp_id = data.get("id") if data else None
    if not exp_id:
        return jsonify(success=False, error="No id provided"), 400

    cursor.execute("DELETE FROM expenses WHERE id=%s", (exp_id,))
    conn.commit()

    cursor.execute("SELECT COALESCE(SUM(amount),0) FROM expenses")
    total = cursor.fetchone()[0]

    # Always return pure JSON
    return jsonify(success=True, total=float(total))


if __name__ == "__main__":
    app.run(debug=True)

