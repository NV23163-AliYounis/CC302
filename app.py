from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# In-memory todo list
todos = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        task = request.form.get("task")
        if task:
            todos.append(task)
        return redirect(url_for("index"))
    return render_template("index.html", todos=todos)

@app.route("/delete/<int:task_id>")
def delete(task_id):
    if 0 <= task_id < len(todos):
        todos.pop(task_id)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
