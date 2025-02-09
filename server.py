import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Plik do przechowywania sesji
SESSIONS_FILE = "sessions.json"

# Ładowanie sesji z pliku
def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
    return {}

# Zapisywanie sesji do pliku
def save_sessions():
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)

# Załadowanie istniejących sesji
sessions = load_sessions()

@app.route('/')
def home():
    return "Relay Server is running!", 200

# 🔹 REJESTRACJA HOSTA
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data or "code" not in data:
            return jsonify({"status": "ERROR", "message": "Invalid request"}), 400
        
        code = data["code"]
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)  # Pobiera IP hosta
        
        if not code or not ip:
            return jsonify({"status": "ERROR", "message": "Missing data"}), 400
        
        sessions[code] = ip
        save_sessions()  # Zapisuje sesję
        print(f"[DEBUG] Nowa sesja: {code} -> {ip}")  # Logi debugowania

        return jsonify({"status": "OK", "message": "Session registered", "ip": ip}), 200
    except Exception as e:
        print(f"[ERROR] Błąd rejestracji: {str(e)}")
        return jsonify({"status": "ERROR", "message": "Server error"}), 500

# 🔹 POBIERANIE IP HOSTA
@app.route('/get_ip', methods=['GET'])
def get_ip():
    try:
        code = request.args.get("code")
        print(f"[DEBUG] Szukam sesji: {code}")

        if not code:
            return jsonify({"status": "ERROR", "message": "No session code provided"}), 400

        if code in sessions:
            return jsonify({"status": "OK", "ip": sessions[code]}), 200
        
        return jsonify({"status": "ERROR", "message": "Session not found"}), 404
    except Exception as e:
        print(f"[ERROR] Błąd pobierania IP: {str(e)}")
        return jsonify({"status": "ERROR", "message": "Server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
