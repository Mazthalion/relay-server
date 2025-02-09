import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Plik do przechowywania sesji
SESSIONS_FILE = "sessions.json"

# Ładowanie zapisanych sesji
def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[ERROR] Błąd odczytu JSON, resetowanie sesji!")
            return {}
    return {}

# Zapisywanie sesji do pliku
def save_sessions():
    try:
        with open(SESSIONS_FILE, "w") as f:
            json.dump(sessions, f)
        print("[DEBUG] Sesje zapisane!")
    except Exception as e:
        print(f"[ERROR] Nie udało się zapisać sesji: {e}")

sessions = load_sessions()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)  # Wymusza parsowanie JSON
    print(f"[DEBUG] Otrzymano dane: {data}")  # 🛠 Debugging

    if not data or "code" not in data:
        return jsonify({"status": "ERROR", "message": "Brak kodu sesji w żądaniu"}), 400

    code = str(data["code"]).strip()  # Konwersja kodu na string i usunięcie spacji
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    if code and ip:
        sessions[code] = ip
        save_sessions()
        print(f"[DEBUG] Dodano sesję: {code} -> {ip}")  # 🛠 Debugging
        return jsonify({"status": "OK", "message": "Session registered", "ip": ip}), 200

    return jsonify({"status": "ERROR", "message": "Niepoprawne dane"}), 400

@app.route('/get_ip', methods=['GET'])
def get_ip():
    code = request.args.get('code')
    print(f"[DEBUG] Sprawdzam sesję dla kodu: {code}")  # Debug w logach

    if not code:
        return jsonify({"status": "ERROR", "message": "Brak kodu w zapytaniu"}), 400

    if code in sessions:
        return jsonify({"status": "OK", "ip": sessions[code]}), 200
    
    return jsonify({"status": "ERROR", "message": "Sesja nie istnieje"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Pobiera port z ustawień Render
    app.run(host="0.0.0.0", port=port, debug=True)
