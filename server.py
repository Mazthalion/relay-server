from flask import Flask, request, jsonify

app = Flask(__name__)

# Przechowywanie kodów sesji i IP hostów
sessions = {}

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    code = data.get('code')
    ip = request.remote_addr  # Pobiera publiczny IP hosta

    if code and ip:
        sessions[code] = ip
        return jsonify({"status": "OK", "message": "Session registered"}), 200
    return jsonify({"status": "ERROR", "message": "Invalid data"}), 400

@app.route('/get_ip', methods=['GET'])
def get_ip():
    code = request.args.get('code')
    if code in sessions:
        return jsonify({"ip": sessions[code]}), 200
    return jsonify({"status": "ERROR", "message": "Session not found"}), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
