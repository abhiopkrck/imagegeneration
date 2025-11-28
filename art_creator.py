from flask import Flask, render_template, request, jsonify
from bytez import Bytez
import json
import os
from datetime import datetime

app = Flask(__name__)

# ==== CONFIG ====
BYTEZ_API_KEY = "ea0e20284203b535479c427e0d609c77"
MODEL_NAME = "google/imagen-4.0-ultra-generate-001"

sdk = Bytez(BYTEZ_API_KEY)
model = sdk.model(MODEL_NAME)

DB_FILE = "data.json"


# ---------- JSON DATABASE FUNCTIONS ----------
def init_db():
    """Create database file if missing"""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump([], f, indent=4)


def load_db():
    """Load all saved image entries"""
    with open(DB_FILE, "r") as f:
        return json.load(f)


def save_entry(prompt, image_url):
    """Add new entry to JSON database"""
    db = load_db()

    new_id = db[-1]["id"] + 1 if db else 1

    entry = {
        "id": new_id,
        "prompt": prompt,
        "image_url": image_url,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    db.append(entry)

    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

    return entry


# Create DB on first run
init_db()


# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    prompt = request.json.get("prompt")

    try:
        result = model.run(prompt)

        if result and hasattr(result, "output"):
            image_url = result.output

            # Save to JSON database
            entry = save_entry(prompt, image_url)

            return jsonify({"success": True, "entry": entry})

        return jsonify({"success": False})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/history")
def history():
    """Return full database"""
    db = load_db()
    return jsonify(db)


if __name__ == "__main__":
    app.run(debug=True)
