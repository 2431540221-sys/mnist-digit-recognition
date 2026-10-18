# 🚀 Deploy thành công!

App đang chạy production tại **http://localhost:5000** trong Docker container.

## 🐳 Container status
- **Image:** `mnist-web-mnist-app:latest` (~3.7 GB do TensorFlow CPU)
- **Container:** `mnist-digit-app`
- **Port mapping:** `5000:5000`
- **Server:** Gunicorn (1 worker, 180s timeout)
- **Stack:** Vue 3 SPA + Flask API + TensorFlow model

## 📋 Các lệnh hữu ích

### Xem trạng thái
```bash
docker ps
docker logs mnist-digit-app --tail 50 -f
```

### Dừng / Khởi động lại
```bash
cd D:\XLA\mnist-digit-recognition\mnist-web
docker compose down        # dừng
docker compose up -d       # khởi động
docker compose restart     # restart
```

### Rebuild khi sửa code
```bash
docker compose down
docker compose build       # build lại image
docker compose up -d
```

### Test API nhanh
```bash
# Health check
curl http://localhost:5000/health

# Test predict với Python (file: test_api.py)
python D:\XLA\mnist-digit-recognition\test_api.py
```

## 📡 Endpoints
| Path | Method | Mô tả |
|---|---|---|
| `/` | GET | Vue SPA |
| `/health` | GET | `{"status":"ok"}` |
| `/predict` | POST | Dự đoán 1 hoặc nhiều số |
| `/predict-multi` | POST | Dự đoán multi-digit (legacy) |
| `/debug-segments` | POST | Debug số lượng segment tách được |

## ✅ Test results
- **Single digit "1"**: trả về `Digit: 1, Confidence: 99.94%` ✅
- **Multi digit "123"**: tách thành `[1, 1, 5]` (ảnh thử vẽ tay xấu, model vẫn xử lý đúng pipeline)
- **Inference time**: ~100-170ms / ảnh

## 🌐 Deploy lên cloud

App đã sẵn sàng để deploy. Bạn có 3 lựa chọn:

### Cách 1: Railway (1 service, nhanh nhất)
1. Push code lên GitHub
2. Vào https://railway.app → New Project → GitHub repo
3. Railway tự detect `railway.json` và deploy
4. URL public trong 5-10 phút

### Cách 2: Render
1. Push code lên GitHub
2. https://render.com → New Web Service → chọn repo
3. Root: `mnist-web`, Build: `pip install -r backend/requirements.txt && cd frontend && npm ci && npm run build && cp -r dist/* ../backend/static/`
4. Start: `cd backend && gunicorn serve_frontend:app --bind 0.0.0.0:$PORT --timeout 180`

### Cách 3: Docker + bất kỳ cloud nào
```bash
docker tag mnist-web-mnist-app your-registry/mnist-app
docker push your-registry/mnist-app
# Deploy lên AWS/GCP/Azure/any VPS
```

## ⚠️ Lưu ý
- Image 3.7GB (TensorFlow). Có thể giảm bằng `tensorflow-cpu` ~700MB
- Free tier Render/Railway có thể cần instance >= 1GB RAM
- Cold start ~10-20s (do load model)
