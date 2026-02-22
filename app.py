import importlib.util
import os

# Load the Flask app from .vscode/app.py without running the __main__ block
spec = importlib.util.spec_from_file_location("todo_app_module", os.path.join(os.path.dirname(__file__), ".vscode", "app.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Expose `app` for tests and CI
app = getattr(module, "app")

if __name__ == "__main__":
    # Run the app when executed directly
    app.run(host="0.0.0.0", port=5000, debug=True)
