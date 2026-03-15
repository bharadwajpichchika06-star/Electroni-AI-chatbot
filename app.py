from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import json
import os
from datetime import datetime

app = Flask(__name__)

genai.configure(api_key="AIzaSyCQXUcqiXojKpTfuFW_yVx8pWy0icy8NOY")
model = genai.GenerativeModel("gemini-2.5-flash")

HISTORY_FILE = "chat_history.json"

ELECTRONICS_KEYWORDS = [
    "mobile", "phone", "smartphone", "iphone", "android", "samsung", "oneplus", "xiaomi",
    "laptop", "computer", "pc", "mac", "macbook", "dell", "hp", "lenovo", "asus", "acer",
    "bluetooth", "headphone", "earphone", "earbud", "airpod", "speaker",
    "tablet", "ipad", "kindle",
    "tv", "television", "monitor", "display", "screen",
    "camera", "dslr", "mirrorless", "gopro",
    "smartwatch", "watch", "wearable", "fitbit",
    "router", "wifi", "modem", "network",
    "keyboard", "mouse", "trackpad",
    "charger", "battery", "power bank", "adapter",
    "processor", "cpu", "gpu", "ram", "ssd", "hard disk", "storage",
    "printer", "scanner",
    "drone", "robot",
    "refrigerator", "washing machine", "microwave", "air conditioner", "ac",
    "gaming", "console", "playstation", "xbox", "nintendo",
    "usb", "cable", "port", "hdmi",
    "led", "oled", "amoled",
    "5g", "4g", "lte",
    "chip", "circuit", "semiconductor", "electronic",
    "gadget", "device", "tech", "technology",
]

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def is_electronics_related(message):
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in ELECTRONICS_KEYWORDS)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    history = load_history()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not is_electronics_related(user_message):
        bot_reply = "⚡ Please ask about electronics only! I can help you with mobiles, laptops, Bluetooth devices, TVs, cameras, smartwatches, and other electronic gadgets."
        entry = {
            "session_id": session_id,
            "timestamp": timestamp,
            "user": user_message,
            "bot": bot_reply,
            "filtered": True
        }
        history.append(entry)
        save_history(history)
        return jsonify({"reply": bot_reply, "timestamp": timestamp})

    system_prompt = (
        "You are an expert electronics assistant. You ONLY answer questions about electronic devices and technology "
        "such as mobiles, smartphones, laptops, computers, Bluetooth devices, headphones, tablets, TVs, cameras, "
        "smartwatches, gaming consoles, routers, and all kinds of electronic gadgets and components. "
        "Provide detailed, accurate, and helpful information. Be concise but thorough."
    )

    try:
        full_prompt = f"{system_prompt}\n\nUser question: {user_message}"
        response = model.generate_content(full_prompt)
        bot_reply = response.text

        entry = {
            "session_id": session_id,
            "timestamp": timestamp,
            "user": user_message,
            "bot": bot_reply,
            "filtered": False
        }
        history.append(entry)
        save_history(history)

        return jsonify({"reply": bot_reply, "timestamp": timestamp})

    except Exception as e:
        app.logger.exception("Error generating response")
        return jsonify({"error": "Failed to generate response", "details": str(e)}), 500

@app.route("/history", methods=["GET"])
def get_history():
    history = load_history()
    return jsonify(history)

@app.route("/clear_history", methods=["POST"])
def clear_history():
    save_history([])
    return jsonify({"status": "cleared"})

@app.route("/history/<int:index>", methods=["DELETE"])
def delete_history(index):
    history = load_history()
    if 0 <= index < len(history):
        history.pop(index)
        save_history(history)
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Invalid index"}), 400

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
