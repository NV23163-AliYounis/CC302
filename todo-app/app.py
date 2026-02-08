import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os

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
        db.execute(
            """
            INSERT INTO todos (task, category, priority, due_datetime)
            VALUES (?, ?, ?, ?)
            """,
            (
                request.form["task"],
                request.form["category"],
                request.form["priority"],
                request.form["due_datetime"],
            ),
        )
        db.commit()
        return redirect(url_for("index"))

    filter_type = request.args.get("filter", "all")

    query = "SELECT * FROM todos"
    if filter_type == "active":
        query += " WHERE completed = 0"
    elif filter_type == "completed":
        query += " WHERE completed = 1"

    query += " ORDER BY due_datetime ASC"

    todos = db.execute(query).fetchall()
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
    db = get_db()
    db.execute(
        """
        UPDATE todos
        SET task=?, category=?, priority=?, due_datetime=?, version=version+1
        WHERE id=?
        """,
        (
            request.form["task"],
            request.form["category"],
            request.form["priority"],
            request.form["due_datetime"],
            id,
        ),
    )
    db.commit()
    db.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            category TEXT,
            priority TEXT,
            due_datetime TEXT,
            completed INTEGER,
            version INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    db.close()
    app.run(debug=True)
