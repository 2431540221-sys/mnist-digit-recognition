"""
Entry point cho Vercel Serverless.
Vercel gọi `app` từ module này. Toàn bộ route logic nằm ở `app.py`.
Lưu ý: Vercel serverless có giới hạn 50MB bundle + timeout 10s,
không phù hợp với TensorFlow model ~1-5MB h5. Nên dùng Render/Railway thay thế.
File này giữ để tiện tham khảo.
"""
import sys
import os

# Đảm bảo import được các module local
sys.path.insert(0, os.path.dirname(__file__))

from app import app  # noqa: F401,E402
