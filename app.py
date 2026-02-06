import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_PATH = "data/todos.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()

    if request.method == "POST":
        task = request.form["task"]
        priority = request.form["priority"]
        due_date = request.form["due_date"]

        db.execute(
            "INSERT INTO todos (task, priority, due_date, completed) VALUES (?, ?, ?, 0)",
            (task, priority, due_date),
        )
        db.commit()

    filter_type = request.args.get("filter", "all")

    if filter_type == "completed":
        todos = db.execute("SELECT * FROM todos WHERE completed = 1").fetchall()
    elif filter_type == "active":
        todos = db.execute("SELECT * FROM todos WHERE completed = 0").fetchall()
    else:
        todos = db.execute("SELECT * FROM todos").fetchall()

    db.close()
    return render_template("index.html", todos=todos, filter_type=filter_type)


@app.route("/complete/<int:id>")
def complete(id):
    db = get_db()
    db.execute("UPDATE todos SET completed = 1 WHERE id = ?", (id,))
    db.commit()
    db.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:id>")
def delete(id):
    db = get_db()
    db.execute("DELETE FROM todos WHERE id = ?", (id,))
    db.commit()
    db.close()
    return redirect(url_for("index"))


@app.route("/edit/<int:id>", methods=["POST"])
def edit(id):
    task = request.form["task"]
    priority = request.form["priority"]
    due_date = request.form["due_date"]

    db = get_db()
    db.execute(
        "UPDATE todos SET task=?, priority=?, due_date=? WHERE id=?",
        (task, priority, due_date, id),
    )
    db.commit()
    db.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    import os

    os.makedirs("data", exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            priority TEXT,
            due_date TEXT,
            completed INTEGER
        )"""
    )
    db.close()

    app.run(host="0.0.0.0", port=5000)
