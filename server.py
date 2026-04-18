from flask import Flask, request, jsonify, send_from_directory, session, make_response
from werkzeug.utils import secure_filename
import json
import os
import time
import secrets
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Secret key: must be set via SESSION_SECRET or SECRET_KEY env var.
# If missing, generate a random one (sessions reset on restart — acceptable fallback).
_secret = os.environ.get('SESSION_SECRET') or os.environ.get('SECRET_KEY')
if not _secret:
    logging.warning('SESSION_SECRET not set — generating a random key. Sessions will reset on restart.')
    _secret = secrets.token_hex(32)
app.secret_key = _secret

# Session cookie security
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # set True behind HTTPS in production

# Limit file uploads to 100 MB
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'chainan2002')
TEAS_FILE = os.path.join(os.path.dirname(__file__), 'teas.json')
CONTENT_FILE = os.path.join(os.path.dirname(__file__), 'content.json')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'mov', 'ogv'}

# File types that must never be served via the static route
BLOCKED_EXTENSIONS = {'.py', '.json', '.toml', '.lock', '.md', '.txt', '.ini', '.cfg', '.env'}
BLOCKED_PREFIXES = ('.', '__')

def load_teas():
    with open(TEAS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_teas(data):
    tmp = TEAS_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, TEAS_FILE)

def load_content():
    try:
        with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"modals": {}, "teas": {}, "footer": {}}

def save_content(data):
    tmp = CONTENT_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, CONTENT_FILE)

def serve_html(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    response = make_response(content)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Serve static files from root
@app.route('/')
def index():
    return serve_html('index.html')

@app.route('/admin')
def admin():
    return serve_html('admin.html')

@app.route('/<path:filename>')
def static_files(filename):
    # Block access to sensitive file types and hidden files
    parts = filename.split('/')
    for part in parts:
        if any(part.startswith(p) for p in BLOCKED_PREFIXES):
            return jsonify({'error': 'Forbidden'}), 403
    ext = os.path.splitext(filename)[1].lower()
    if ext in BLOCKED_EXTENSIONS:
        return jsonify({'error': 'Forbidden'}), 403
    return send_from_directory('.', filename)

# --- API ---

@app.route('/api/teas', methods=['GET'])
def get_teas():
    return jsonify(load_teas())

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if data and data.get('password') == ADMIN_PASSWORD:
        session['logged_in'] = True
        return jsonify({'ok': True})
    # Small delay on failure to slow brute-force
    time.sleep(0.5)
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
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Нет данных'}), 400
    save_teas(data)
    return jsonify({'ok': True})

@app.route('/api/content', methods=['GET'])
def get_content():
    return jsonify(load_content())

@app.route('/api/content', methods=['POST'])
def update_content():
    if not session.get('logged_in'):
        return jsonify({'error': 'Не авторизован'}), 401
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Нет данных'}), 400
    save_content(data)
    # Also sync varieties to teas.json for backward compatibility
    if 'teas' in data:
        try:
            teas = load_teas()
            for key, tea in data['teas'].items():
                if 'varieties' in tea:
                    teas[key] = tea['varieties']
            save_teas(teas)
        except Exception:
            pass
    return jsonify({'ok': True})

@app.route('/api/upload', methods=['POST'])
def upload_image():
    if not session.get('logged_in'):
        return jsonify({'error': 'Не авторизован'}), 401
    if 'file' not in request.files:
        return jsonify({'error': 'Нет файла'}), 400
    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({'error': 'Недопустимый формат. Разрешены: jpg, jpeg, png, gif, webp, mp4, webm, mov, ogv'}), 400
    media_prefix = 'video' if ext in {'mp4', 'webm', 'mov', 'ogv'} else 'img'
    new_name = f"{media_prefix}_{time.time_ns()}.{ext}"
    file.save(os.path.join(os.path.dirname(__file__), new_name))
    return jsonify({'ok': True, 'url': f'/{new_name}'})

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Файл слишком большой. Максимум 100 МБ.'}), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
