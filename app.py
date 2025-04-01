print(">>> app.py started")
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# Replace with your actual OpenAI API key

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Set up system prompt to behave like El Rayo's assistant
        response = client.chat.completions.create(model="gpt-4",  # You can also use gpt-3.5-turbo
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a friendly, knowledgeable assistant for El Rayo, "
                    "a vibrant Mexican restaurant located in Portland, Maine. "
                    "You help customers with questions about hours, menu items, reservations, "
                    "takeout, dietary restrictions, location, parking, and general info. "
                    "If someone asks about things you don’t know, kindly redirect them to call or visit."
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ])

        reply = response.choices[0].message.content.strip()
        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)