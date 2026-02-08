import sqlite3
from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)
DB_PATH = "data/nv23163_todo.db"
APP_VERSION = "1.0.0"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            task_type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Planned',
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()

    if request.method == "POST":
        db.execute("""
            INSERT INTO tasks (title, task_type, status, start_time, end_time)
            VALUES (?, ?, ?, ?, ?)
        """, (
            request.form["title"],
            request.form["task_type"],
            request.form["status"],
            request.form["start_time"],
            request.form["end_time"],
        ))
        db.commit()
        return redirect(url_for("index"))

    tasks = db.execute(
        "SELECT * FROM tasks ORDER BY start_time ASC"
    ).fetchall()
    db.close()

    return render_template("index.html", tasks=tasks, version=APP_VERSION)


@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    db = get_db()
    db.execute("""
        UPDATE tasks
        SET title = ?,
            task_type = ?,
            status = ?,
            start_time = ?,
            end_time = ?,
            version = version + 1,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        request.form["title"],
        request.form["task_type"],
        request.form["status"],
        request.form["start_time"],
        request.form["end_time"],
        id,
    ))
    db.commit()
    db.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:id>")
def delete(id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", (id,))
    db.commit()
    db.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
