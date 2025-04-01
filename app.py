print(">>> app.py started")
from flask import Flask, request, jsonify
from openai import OpenAI
from vercel_wsgi import handle_request
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = client.chat.completions.create(model="gpt-4",
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

def handler(environ, start_response):
    return handle_request(app, environ, start_response)