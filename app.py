import json
import os
from pathlib import Path
from flask import Flask, jsonify, request

# Load cupcake order records
RECORDS = json.loads(Path(__file__).with_name("records.json").read_text())
LOOKUP = {r["id"]: r for r in RECORDS}

app = Flask(__name__)

@app.route("/")
def index():
    """Simple index route to verify the API is running."""
    return jsonify({"message": "Cupcake MCP API"})

@app.route("/search", methods=["POST"])
def search():
    """Search for cupcake orders by keyword."""
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    tokens = query.lower().split()
    results = []
    for r in RECORDS:
        hay = " ".join([
            r.get("title", ""),
            r.get("text", ""),
            " ".join(r.get("metadata", {}).values()),
        ]).lower()
        if any(t in hay for t in tokens):
            results.append({
                "id": r["id"],
                "title": r.get("title", ""),
                "text": r.get("text", ""),
            })
    return jsonify({"results": results})

@app.route("/fetch/<id>")
def fetch(id: str):
    """Fetch a cupcake order by ID."""
    if id not in LOOKUP:
        return jsonify({"error": "unknown id"}), 404
    r = LOOKUP[id]
    result = {
        "id": r["id"],
        "title": r.get("title", ""),
        "text": r.get("text", ""),
        "url": r.get("url"),
        "metadata": r.get("metadata"),
    }
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
