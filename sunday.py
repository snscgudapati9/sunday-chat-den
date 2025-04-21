from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import datetime
import pyttsx3
from difflib import get_close_matches

app = Flask(__name__)

# Files
MEMORY_FILE = 'memory.json'
DEFAULT_MEMORY_FILE = 'default_memory.json'
CHAT_LOG = 'chat_log.txt'

# Hardcoded Knowledge Base
knowledge_base = {
    "RCM": {
        "aliases": ["REVENUE CYCLE MANAGEMENT", "RCM"],
        "definition": "Revenue Cycle Management (RCM) is the process healthcare systems use to track patient care episodes from registration to final payment.",
        "steps": [
            "1. Patient registration",
            "2. Insurance verification",
            "3. Charge capture",
            "4. Claim submission",
            "5. Payment posting",
            "6. Denial management",
            "7. Reporting"
        ],
        "importance": [
            "Improves financial performance",
            "Reduces claim denials",
            "Enhances patient experience"
        ]
    },
    "PHYSICIAN BILLING": {
        "aliases": ["PHYSICIAN BILLING", "DOCTOR BILLING"],
        "definition": "Physician billing refers to billing for services by doctors like consultations and procedures.",
        "steps": [
            "1. Document services provided",
            "2. Assign medical codes",
            "3. Generate and submit claims",
            "4. Follow up on payments",
            "5. Post payments and manage denials"
        ]
    }
}

# Load memory (trainable data)
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    elif os.path.exists(DEFAULT_MEMORY_FILE):
        with open(DEFAULT_MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {}

memory = load_memory()

# Save memory
def save_memory():
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)

# Fuzzy match hardcoded knowledge
def find_knowledge_match(user_input):
    user_input = user_input.strip().upper()
    all_terms = {alias: key for key, data in knowledge_base.items() for alias in data.get("aliases", [])}
    match = get_close_matches(user_input, all_terms.keys(), n=1, cutoff=0.6)
    if match:
        return all_terms[match[0]]
    return None

# Generate response
def get_response(user_input):
    user_input_lower = user_input.lower().strip()

    # Check hardcoded knowledge base
    match_key = find_knowledge_match(user_input)
    if match_key:
        topic = knowledge_base[match_key]
        response = ""

        if "definition" in topic:
            response += f"Definition:\n{topic['definition']}\n\n"
        if "steps" in topic:
            response += "Steps:\n" + "\n".join(topic["steps"]) + "\n\n"
        if "importance" in topic:
            response += "Importance:\n" + "\n".join(topic["importance"]) + "\n\n"
        return response.strip()

    # Check memory
    for key in memory:
        if key.lower() in user_input_lower:
            return memory[key]

    return "Sorry, mama I don't know that yet. Train me?"

# Text-to-speech
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Chat logging
def log_interaction(user, sunday):
    with open(CHAT_LOG, 'a') as f:
        f.write(f"You: {user}\nSunday: {sunday}\n\n")

# Routes
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
    today = datetime.datetime.now()
    if today.weekday() < 5:
        return jsonify({
            'task': 'Complete Sunday’s next feature update.',
            'date': today.strftime("%d/%m/%Y")
        })
    return jsonify({'task': None})

@app.route('/save_chat', methods=['POST'])
def save_chat():
    data = request.json
    with open("chat_log.txt", "a") as f:
        f.write(json.dumps(data) + "\n")
    return jsonify({"status": "saved"})

@app.route('/download_memory')
def download_memory():
    return send_file(MEMORY_FILE, as_attachment=True)

# Run app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
