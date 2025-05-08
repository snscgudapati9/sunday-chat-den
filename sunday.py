from flask import Flask, request, jsonify, send_from_directory
import openai
import os

app = Flask(__name__)

# OpenRouter API Key and Base URL
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"  # OpenRouter API Base URL

@app.route('/')
def index():
    return send_from_directory(os.path.join(os.getcwd(), 'templates'), 'index.html')

@app.route('/ask', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({"response": "Please provide a message."}), 400

        # Requesting response from OpenRouter/OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Sunday, a helpful and funny assistant."},
                {"role": "user", "content": user_message}
            ]
        )

        answer = response['choices'][0]['message']['content'].strip()

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
    app.run(debug=True, use_reloader=False)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
