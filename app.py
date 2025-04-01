import logging
from flask import Flask, request, jsonify
from openai import OpenAI
import os

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logging.debug("app.py started")

# Initialize OpenAI client using environment variable for API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("OPENAI_API_KEY environment variable is missing!")
client = OpenAI(api_key=api_key)

# Initialize Flask app
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "El Rayo Chatbot is running!"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4",
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
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app using Flask's default WSGI server for Render

if __name__ == "__main__":
    app.run()