import logging
from flask import Flask, request, jsonify, session
import openai
import os
from openai import OpenAI

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logging.debug("app.py started")

# Initialize OpenAI client using environment variable for API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("OPENAI_API_KEY environment variable is missing!")

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for session support

@app.route("/", methods=["GET"])
def home():
    return """
    <html>
        <head>
            <title>El Rayo Chatbot</title>
            <style>
                body {
                    background-color: #45C4B0;
                    font-family: 'Trebuchet MS', sans-serif;
                    text-align: center;
                    color: #333;
                    padding-top: 50px;
                }
                .container {
                    background-color: white;
                    max-width: 500px;
                    margin: auto;
                    padding: 30px;
                    border-radius: 12px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.2);
                }
                img {
                    width: 200px;
                    margin-bottom: 20px;
                }
                input[type="text"] {
                    width: 90%;
                    padding: 10px;
                    margin-bottom: 20px;
                    border: 1px solid #ccc;
                    border-radius: 6px;
                    font-size: 16px;
                }
                input[type="submit"] {
                    background-color: #E85A4F;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 6px;
                    font-size: 16px;
                    cursor: pointer;
                }
                input[type="submit"]:hover {
                    background-color: #d24a3b;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <img src="/static/logo.png" alt="El Rayo Logo">
                <h1>Ask El Rayo Chatbot</h1>
                <form action="/chat" method="post">
                    <input type="text" id="message" name="message" placeholder="Type your question here..." required><br>
                    <input type="submit" value="Send">
                </form>
            </div>
        </body>
    </html>
    """

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if 'history' not in session:
        session['history'] = []

    data = request.get_json() if request.is_json else request.form
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for El Rayo, a vibrant Mexican restaurant in Portland, Maine."},
                *session['history'],
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content.strip()

        # Append to chat history
        session['history'].append({"role": "user", "content": user_message})
        session['history'].append({"role": "assistant", "content": reply})

        if not request.is_json:
            # Convert chat history to HTML
            history_html = "<br>".join(
                f"<b>You:</b> {m['content']}" if m["role"] == "user" else f"<b>Bot:</b> {m['content']}"
                for m in session['history']
            )
            return f"""
                <div style='text-align: left; max-width: 500px; margin: auto;'>
                    {history_html}
                    <br><br><a href="/">Back</a>
                </div>
            """
        return jsonify({"response": reply})

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route("/reset")
def reset():
    session.pop('history', None)
    return '<p>Chat reset. <a href="/">Start again</a></p>'

# Run the app using Flask's default WSGI server for Render
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)