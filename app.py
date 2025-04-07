import logging
from flask import Flask, request, jsonify, session
import openai
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logging.debug("app.py started")

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
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }

                @keyframes bubbleIn {
                    from { opacity: 0; transform: scale(0.95); }
                    to { opacity: 1; transform: scale(1); }
                }

                @keyframes blink {
                    0% { opacity: 0.2; }
                    20% { opacity: 1; }
                    100% { opacity: 0.2; }
                }

                .typing {
                    display: inline-block;
                    margin-left: 10px;
                }

                .typing span {
                    display: inline-block;
                    background: #F0F0F0;
                    border-radius: 50%;
                    width: 8px;
                    height: 8px;
                    margin: 0 2px;
                    animation: blink 1.4s infinite both;
                }

                .typing span:nth-child(2) {
                    animation-delay: 0.2s;
                }

                .typing span:nth-child(3) {
                    animation-delay: 0.4s;
                }

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
                    animation: fadeIn 0.6s ease-out;
                }
                .chat-window {
                    max-height: 400px;
                    overflow-y: auto;
                    margin-top: 20px;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                .bubble {
                    animation: bubbleIn 0.3s ease-out;
                    text-align: left;
                    margin-bottom: 10px;
                    padding: 12px 16px;
                    border-radius: 12px;
                }
                .bubble.user {
                    align-self: flex-end;
                    background-color: #E85A4F;
                    color: white;
                }
                .bubble.bot {
                    align-self: flex-start;
                    background-color: #f0f0f0;
                    color: #000;
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
                <div class="chat-window"></div>
            </div>
            <script>
                const chatWindow = document.createElement("div");
                chatWindow.className = "chat-window";
                document.querySelector(".container").appendChild(chatWindow);

                document.querySelector("form").addEventListener("submit", async function(e) {
                    e.preventDefault();
                    const input = document.getElementById("message");
                    const message = input.value.trim();
                    if (!message) return;

                    const userBubble = document.createElement("div");
                    userBubble.className = "bubble user";
                    userBubble.innerHTML = `<strong>You:</strong> ${message}`;
                    chatWindow.appendChild(userBubble);

                    const typingBubble = document.createElement("div");
                    typingBubble.className = "bubble bot";
                    typingBubble.innerHTML = `<strong>El Rayo:</strong> <span class='typing'><span></span><span></span><span></span></span>`;
                    chatWindow.appendChild(typingBubble);
                    chatWindow.scrollTop = chatWindow.scrollHeight;

                    input.value = "";

                    const res = await fetch("/chat", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ message })
                    });

                    const data = await res.json();
                    typingBubble.remove();

                    const botBubble = document.createElement("div");
                    botBubble.className = "bubble bot";
                    botBubble.innerHTML = `<strong>El Rayo:</strong> ${data.response || "Sorry, something went wrong."}`;
                    chatWindow.appendChild(botBubble);
                    chatWindow.scrollTop = chatWindow.scrollHeight;
                });
            </script>
        </body>
    </html>
    """

@app.route("/chat", methods=["POST"])
def chat():
    if 'history' not in session:
        session['history'] = []

    data = request.get_json() if request.is_json else request.form
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for El Rayo, a vibrant Mexican restaurant in Portland, Maine."},
                *session['history'],
                {"role": "user", "content": user_message}
            ]
        )

        reply = response.choices[0].message.content.strip()
        session['history'].append({"role": "user", "content": user_message})
        session['history'].append({"role": "assistant", "content": reply})
        return jsonify({"response": reply})

    except Exception as e:
        logging.error(f"Chat error: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route("/reset")
def reset():
    session.pop('history', None)
    return '<p>Chat reset. <a href="/">Start again</a></p>'

# Run the app using Flask's default WSGI server for Render
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)