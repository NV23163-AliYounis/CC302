"""
TODO-APP PROJECT STATUS

FINISHED TASKS:
  ✓ Database schema creation (SQLite)
  ✓ Task CRUD operations (Create, Read, Update, Delete)
  ✓ Flask routing setup (index, update, delete routes)
  ✓ HTML template rendering with Jinja2
  ✓ Docker containerization
  ✓ Task sorting by start_time

PENDING TASKS:
  ◐ Task filtering by status (need UI implementation)
  ◐ Task search functionality
  ◐ User authentication system
  ◐ Task priority levels
  ◐ Export tasks to CSV/PDF

CANCELED TASKS:
  ✗ Real-time synchronization with WebSocket
  ✗ Multi-user collaboration features
  ✗ Mobile app version

MISSING TASKS:
  ○ Task dependencies/subtasks
  ○ Recurring tasks support
  ○ Task notes/comments section
  ○ File attachments for tasks
  ○ Task statistics dashboard
  ○ Email notifications
  ○ Dark mode theme
  ○ Backup/restore functionality
"""

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

    # Support filtering by status via query parameter e.g. ?status=Done
    selected_status = request.args.get("status", "All")
    search_q = request.args.get("q", "").strip()

    # Build query dynamically based on provided filters
    if selected_status and selected_status != "All" and search_q:
        tasks = db.execute(
            "SELECT * FROM tasks WHERE status = ? AND title LIKE ? ORDER BY start_time ASC",
            (selected_status, f"%{search_q}%")
        ).fetchall()
    elif selected_status and selected_status != "All":
        tasks = db.execute(
            "SELECT * FROM tasks WHERE status = ? ORDER BY start_time ASC",
            (selected_status,)
        ).fetchall()
    elif search_q:
        tasks = db.execute(
            "SELECT * FROM tasks WHERE title LIKE ? ORDER BY start_time ASC",
            (f"%{search_q}%",)
        ).fetchall()
    else:
        tasks = db.execute(
            "SELECT * FROM tasks ORDER BY start_time ASC"
        ).fetchall()

    db.close()

    return render_template(
        "index.html",
        tasks=tasks,
        version=APP_VERSION,
        selected_status=selected_status,
        q=search_q,
    )


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
