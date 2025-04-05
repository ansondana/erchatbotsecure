import logging
from flask import Flask, request, jsonify
import openai
import os

# Initialize logging
logging.basicConfig(level=logging.DEBUG)
logging.debug("app.py started")

# Initialize OpenAI client using environment variable for API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("OPENAI_API_KEY environment variable is missing!")
openai.api_key = api_key

# Initialize Flask app
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return """
    <html>
        <head><title>El Rayo Chatbot</title></head>
        <body>
            <h1>Welcome to El Rayo Chatbot</h1>
            <form action="/chat" method="post">
                <label for="message">Your Message:</label><br>
                <input type="text" id="message" name="message"><br><br>
                <input type="submit" value="Send">
            </form>
        </body>
    </html>
    """

@app.route("/chat", methods=["GET", "POST"])
def chat():
    data = request.get_json() if request.is_json else request.form
    user_message = data.get("message", "")

    if not user_message:  # If no message is provided
        return jsonify({"error": "No message provided"}), 400

    try:
        # Use OpenAI's GPT-4 model to respond based on the user's message
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Specify the model you want to use
            messages=[
                {"role": "system", "content": "You are a helpful assistant for El Rayo, a vibrant Mexican restaurant in Portland, Maine."},
                {"role": "user", "content": user_message}
            ]
        )

        # Extract the response from OpenAI's API response
        reply = response['choices'][0]['message']['content'].strip()

        # Return the response back to the user
        if not request.is_json:
            return f"<p><strong>Response:</strong> {reply}</p>"
        return jsonify({"response": reply})

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Run the app using Flask's default WSGI server for Render
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)