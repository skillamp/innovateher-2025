import os
from flask import Flask, request, jsonify, render_template
from groq import Groq

app = Flask(__name__)

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')  # Render the HTML page

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')  # Get the message from the frontend

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Call Groq API to generate a response
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": user_message}],
            model="llama-3.3-70b-versatile",  # Or whatever model you want to use
        )

        # Extract the response
        chatbot_reply = chat_completion.choices[0].message.content
        return jsonify({'reply': chatbot_reply})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

