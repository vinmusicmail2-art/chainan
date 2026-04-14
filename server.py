from flask import Flask, request, jsonify, send_from_directory, session
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'chainan-secret-2002')

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'chainan2002')
TEAS_FILE = os.path.join(os.path.dirname(__file__), 'teas.json')

def load_teas():
    with open(TEAS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_teas(data):
    with open(TEAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Serve static files from root
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# --- API ---

@app.route('/api/teas', methods=['GET'])
def get_teas():
    return jsonify(load_teas())

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if data and data.get('password') == ADMIN_PASSWORD:
        session['logged_in'] = True
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'error': 'Неверный пароль'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})

@app.route('/api/me', methods=['GET'])
def me():
    return jsonify({'logged_in': session.get('logged_in', False)})

@app.route('/api/teas', methods=['POST'])
def update_teas():
    if not session.get('logged_in'):
        return jsonify({'error': 'Не авторизован'}), 401
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Нет данных'}), 400
    save_teas(data)
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
