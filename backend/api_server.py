from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import send_to_rabbitmq
from datetime import datetime
import os

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "Chat API server is running",
        "endpoints": {
            "send_message": "/api/chat/send (POST)"
        }
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

@app.route("/api/chat/send", methods=["POST", "OPTIONS"])
def send_message():
    if request.method == "OPTIONS":
        return "", 200
        
    if request.is_json:
        data = request.get_json()
    else:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    user_id = data.get("user_id")
    message = data.get("message")
    timestamp = datetime.utcnow().isoformat() + "Z"

    payload = {"user_id": user_id, "message": message, "timestamp": timestamp}
    send_to_rabbitmq(payload)
    return jsonify({"status": "queued", "data": payload}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
