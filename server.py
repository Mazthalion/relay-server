import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Plik do przechowywania sesji
SESSIONS_FILE = "sessions.json"

# Ładowanie zapisanych sesji
def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
    return {}

# Zapisywanie sesji do pliku
def save_sessions():
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)

sessions = load_sessions()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    code = data.get('code')
    
    # Pobiera IP hosta z nagłówków (jeśli jest dostępny)
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    if code and ip:
        sessions[code] = ip
        save_sessions()  # Zapisuje sesję do pliku
        print(f"Session added: {code} -> {ip}")  # Debug w logach
        return jsonify({"status": "OK", "message": "Session registered", "ip": ip}), 200
    return jsonify({"status": "ERROR", "message": "Invalid data"}), 400

@app.route('/get_ip', methods=['GET'])
def get_ip():
    code = request.args.get('code')
    print(f"Checking session: {code}")  # Debug w logach
    print(sessions)  # Wyświetla obecne sesje

    if code in sessions:
        return jsonify({"status": "OK", "ip": sessions[code]}), 200
    return jsonify({"status": "ERROR", "message": "Session not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Pobiera port z ustawień Render
    app.run(host="0.0.0.0", port=port, debug=True)
