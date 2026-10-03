import os
from flask import Flask, jsonify, request

app = Flask(__name__)

NODE_NAME = os.getenv("NODE_NAME", "node")
ROLE = os.getenv("ROLE", "follower")
PORT = int(os.getenv("PORT", "8080"))

# Demo data stored in memory for the TP.
DATA = []

@app.get("/")
def home():
    return jsonify({
        "node": NODE_NAME,
        "role": ROLE,
        "message": "Distributed Data TP"
    })

@app.get("/health")
def health():
    return jsonify({"status": "UP", "node": NODE_NAME, "role": ROLE})

@app.get("/data")
def get_data():
    return jsonify({
        "node": NODE_NAME,
        "role": ROLE,
        "count": len(DATA),
        "data": DATA
    })

@app.post("/data")
def add_data():
    payload = request.get_json(silent=True) or {}
    if "key" not in payload or "value" not in payload:
        return jsonify({"error": "key and value are required"}), 400

    item = {"key": str(payload["key"]), "value": payload["value"]}
    DATA.append(item)

    return jsonify({
        "message": "data stored",
        "node": NODE_NAME,
        "role": ROLE,
        "item": item
    }), 201

@app.delete("/data")
def clear_data():
    DATA.clear()
    return jsonify({"message": "data cleared", "node": NODE_NAME})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
