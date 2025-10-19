from flask import Flask, jsonify, render_template, request, redirect,Response
import mysql.connector
import io
import matplotlib.pyplot as plt
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


def get_expense_data():
    cursor.execute("SELECT category, SUM(amount ) FROM expenses GROUP BY caregory")
    rows=cursor.fetchall()
    categories = [r[0] for r in rows]
    totals= [float(r[1]) for r in rows]
    return categories,totals


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


@app.route("/chart")
def chart():
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()

    categories = [row[0] for row in data]
    totals = [row[1] for row in data]

    plt.figure(figsize=(5,5))
    plt.pie(totals, labels=categories, autopct='%1.1f%%', startangle=140)
    plt.title('Expense Breakdown by Category')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return Response(buf.getvalue(), mimetype='image/png')




if __name__ == "__main__":
    app.run(debug=True)

