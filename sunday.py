from flask import Flask, render_template, request, jsonify
import json
import datetime
import pyttsx3
import os
from flask import send_file  # (already imported Flask)

app = Flask(__name__)

# Files
MEMORY_FILE = 'memory.json'
DEFAULT_MEMORY_FILE = 'default_memory.json'
CHAT_LOG = 'chat_log.txt'

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as file:
            return json.load(file)
    elif os.path.exists(DEFAULT_MEMORY_FILE):
        with open(DEFAULT_MEMORY_FILE, 'r') as file:
            return json.load(file)
    else:
        return {}

memory = load_memory()

def save_memory():
    with open(MEMORY_FILE, 'w') as file:
        json.dump(memory, file, indent=2)

def get_response(user_input):
    user_input = user_input.lower().strip()
    for key in memory:
        if key.lower() in user_input:
            return memory[key]
    return "Sorry, mama I don't know that yet. Train me?"

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def log_interaction(user, sunday):
    with open(CHAT_LOG, 'a') as f:
        f.write(f"You: {user}\nSunday: {sunday}\n\n")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    response = get_response(user_input)
    log_interaction(user_input, response)
    return jsonify({'response': response})

@app.route('/train', methods=['POST'])
def train():
    data = request.json
    question = data.get('question', '').strip()
    answer = data.get('answer', '').strip()
    if question and answer:
        memory[question] = answer
        save_memory()
        return jsonify({'status': 'success', 'message': 'Sunday learned it!'})
    return jsonify({'status': 'error', 'message': 'Invalid input.'})

@app.route('/load_tasks')
def load_tasks():
    # Example logic: only show if it's a weekday
    today = datetime.datetime.now()
    if today.weekday() < 5:  # Mon–Fri
        return jsonify({
            'task': 'Complete Sunday’s next feature update.',
            'date': today.strftime("%d/%m/%Y")
        })
    return jsonify({'task': None})

@app.route("/save_chat", methods=["POST"])
def save_chat():
    data = request.json
    with open("chat_log.txt", "a") as f:
        f.write(json.dumps(data) + "\n")
    return jsonify({"status": "saved"})

@app.route('/download_memory')
def download_memory():
    return send_file(MEMORY_FILE, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Render will set PORT automatically
    app.run(host='0.0.0.0', port=port, debug=True)

