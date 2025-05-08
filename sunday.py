from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI
import os

app = Flask(__name__)

# Setup OpenRouter Client
client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

@app.route('/')
def index():
    return send_from_directory(os.path.join(os.getcwd(), 'templates'), 'index.html')

@app.route('/ask', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({"response": "Please provide a message."}), 400

        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",  # OpenRouter expects vendor prefix
            messages=[
                {"role": "system", "content": "You are Sunday, a helpful and funny assistant."},
                {"role": "user", "content": user_message}
            ]
        )

        answer = response.choices[0].message.content.strip()
        return jsonify({"response": answer})

    except Exception as e:
        return jsonify({"response": f"Oops! Something went wrong. {str(e)}"}), 500

@app.route('/train', methods=['POST'])
def train_sunday():
    data = request.json
    return jsonify({"status": "learned", "data": data}), 200

@app.route('/load_tasks', methods=['GET'])
def load_tasks():
    return jsonify({
        "task": "Update the Sunday's tasks for the next week.",
        "date": "2025-05-07"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
