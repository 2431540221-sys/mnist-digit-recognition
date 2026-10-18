"""
Production server: Flask vừa phục vụ API, vừa serve Vue SPA.
Dùng cho Railway / Render / single-VPS / Docker.

Khi deploy Docker: frontend/dist đã được COPY vào backend/static/.
"""
import os
import sys

# Đảm bảo import được các module local
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory, send_file, Blueprint
from app import app as api_app  # Flask app từ app.py (đã có routes /health, /predict, ...)

# Thư mục build Vue (frontend/dist) — copy sẵn vào image
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')

# ---------- Blueprint cho SPA ----------
# Đăng ký với url_prefix rỗng nhưng ở dưới cùng để API được ưu tiên
spa_bp = Blueprint('spa', __name__)


@spa_bp.route('/', defaults={'path': ''})
@spa_bp.route('/<path:path>')
def spa_fallback(path):
    """
    Catch-all cho Vue SPA routing.
    - Nếu path trỏ tới file tĩnh có thật trong dist → trả file đó.
    - Còn lại → trả index.html để Vue xử lý routing phía client.
    """
    if path:
        full = os.path.join(STATIC_DIR, path)
        if os.path.isfile(full):
            return send_from_directory(STATIC_DIR, path)

    index_path = os.path.join(STATIC_DIR, 'index.html')
    if not os.path.exists(index_path):
        return (
            '<h1>Frontend chưa được build</h1>'
            '<p>Chạy: <code>cd frontend && npm run build</code>, '
            'sau đó copy <code>dist/*</code> vào <code>backend/static/</code>.</p>',
            500,
        )
    return send_file(index_path)


# ---------- Gộp API + SPA ----------
# Tạo app chính, copy config CORS
app = Flask(__name__)
app.config['CORS_HEADERS'] = api_app.config.get('CORS_HEADERS', 'Content-Type')
from flask_cors import CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# 1) Mount toàn bộ route API từ app.py (ưu tiên cao nhất)
for rule in api_app.url_map.iter_rules():
    if rule.endpoint == 'static':
        continue
    # Chỉ re-add những route KHÔNG phải SPA catch-all
    view = api_app.view_functions[rule.endpoint]
    # Thêm vào app chính với cùng path & methods
    app.add_url_rule(
        str(rule),
        endpoint=f'api_{rule.endpoint}',
        view_func=view,
        methods=list(rule.methods - {'HEAD', 'OPTIONS'}),
    )

# 2) Mount SPA blueprint (catch-all, ưu tiên thấp hơn)
app.register_blueprint(spa_bp)

# Alias để gunicorn dùng (`gunicorn serve_frontend:app`)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
