import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Plik do przechowywania sesji
SESSIONS_FILE = "sessions.json"

# 🔹 Funkcja ładowania zapisanych sesji
def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, "r") as f:
                data = json.load(f)
                print(f"[DEBUG] Załadowano sesje: {data}")  # ✅ Logowanie sesji
                return data
        except json.JSONDecodeError:
            print("[ERROR] Błąd odczytu JSON, resetowanie sesji!")
            return {}
    return {}

# 🔹 Funkcja zapisywania sesji
def save_sessions():
    try:
        with open(SESSIONS_FILE, "w") as f:
            json.dump(sessions, f, indent=4)  # ✅ Formatowanie JSON dla czytelności
        print(f"[DEBUG] Sesje zapisane: {sessions}")  # ✅ Debug zapisanych sesji
    except Exception as e:
        print(f"[ERROR] Nie udało się zapisać sesji: {e}")

sessions = load_sessions()

# 🔹 Endpoint do rejestracji hosta (zapisuje jego IP)
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    print(f"[DEBUG] Otrzymano dane: {data}")  # ✅ Logowanie wejściowych danych

    if not data or "code" not in data:
        return jsonify({"status": "ERROR", "message": "Brak kodu sesji w żądaniu"}), 400

    code = str(data["code"]).strip()
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    if code and ip:
        sessions[code] = ip  # 🔹 Zapisujemy IP hosta dla jego kodu
        save_sessions()
        print(f"[DEBUG] Dodano sesję: {code} -> {ip}")  # ✅ Potwierdzenie w logach
        return jsonify({"status": "OK", "message": "Session registered", "ip": ip}), 200

    return jsonify({"status": "ERROR", "message": "Niepoprawne dane"}), 400

# 🔹 Endpoint do pobierania IP hosta na podstawie kodu
@app.route('/get_ip', methods=['GET'])
def get_ip():
    code = request.args.get('code')
    print(f"[DEBUG] Sprawdzam sesję dla kodu: {code}")  # ✅ Logowanie zapytania

    if not code:
        return jsonify({"status": "ERROR", "message": "Brak kodu w zapytaniu"}), 400

    if code in sessions:
        return jsonify({"status": "OK", "ip": sessions[code]}), 200
    
    return jsonify({"status": "ERROR", "message": "Sesja nie istnieje"}), 404

# 🔹 Endpoint testowy - sprawdza wszystkie aktywne sesje (tylko do debugowania)
@app.route('/sessions', methods=['GET'])
def get_sessions():
    return jsonify(sessions)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

