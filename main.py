import os
from flask import Flask, request, jsonify
import google.generativeai as genai
import threading
import time
import requests
from collections import deque

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 0.8,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

chat_sessions = {}

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('q')
        user_id = data.get('id')
        image_url = data.get('image_url')
    else:  # GET request
        query = request.args.get('q')
        user_id = request.args.get('id')
        image_url = None

    if not query or not user_id:
        return jsonify({"error": "Please provide both query and id parameters."}), 400

    if user_id not in chat_sessions:
        chat_sessions[user_id] = {
            "chat": model.start_chat(history=[]),
            "history": deque(maxlen=5)
        }

    chat_session = chat_sessions[user_id]["chat"]
    history = chat_sessions[user_id]["history"]

    history.append(f"User: {query}")

    if image_url:
        response = chat_session.send_message(query, image_url=image_url)
    else:
        response = chat_session.send_message(query)

    history.append(f"Bot: {response.text}")
    return jsonify({"response": response.text})

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "alive"})

def keep_alive():
    # ... (same as your code)
    # Ping your deployed app to keep it awake

if __name__ == '__main__':
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host='0.0.0.0', port=8080) 
