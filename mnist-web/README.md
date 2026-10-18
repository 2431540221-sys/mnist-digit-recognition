# 🧠 MNIST Digit Recognition

Web app nhận diện chữ số viết tay bằng CNN (TensorFlow/Keras).
- **Frontend:** Vue 3 + Vite + Lucide icons
- **Backend:** Flask + TensorFlow
- **AI:** CNN model trained trên MNIST (single & multi-digit)

## 🏗️ Cấu trúc
```
mnist-web/
├── backend/                  # Flask API
│   ├── app.py                # Routes: /predict, /predict-multi, /health
│   ├── serve_frontend.py     # Production: serve cả Vue build
│   ├── preprocessing.py      # Xử lý ảnh, segment multi-digit
│   ├── requirements.txt
│   └── models/
│       └── mnist_cnn_model.h5
├── frontend/                 # Vue 3 SPA
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── Dockerfile                # Multi-stage build
├── docker-compose.yml
├── Procfile                  # Railway/Render/Heroku
├── railway.json
└── docs/                     # Hướng dẫn deploy
    ├── deploy-vercel-render.md
    ├── deploy-railway.md
    └── deploy-docker.md
```

## 🚀 Chạy local

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

## 🌐 Deploy

Có **3 cách** từ dễ → production-grade. Xem chi tiết ở `docs/`:

1. **[Vercel + Render](docs/deploy-vercel-render.md)** — miễn phí, dễ nhất, tách FE/BE
2. **[Railway](docs/deploy-railway.md)** — 1 service, full-stack, $5 credit/tháng
3. **[Docker](docs/deploy-docker.md)** — chạy ở bất kỳ đâu (VPS, GCP, AWS, ...)

## ⚙️ Biến môi trường

### Frontend
- `VITE_API_BASE_URL` — URL backend (mặc định: `/api`)
  - Dev: `/api` (Vite proxy → `localhost:5000`)
  - Prod: `https://your-api.onrender.com` hoặc để trống nếu dùng Railway

### Backend
- `PORT` — port (mặc định: 5000)
- `FLASK_DEBUG` — 0/1 (mặc định: 1)

## 📡 API Endpoints

| Method | Path | Mô tả |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/predict` | Dự đoán (mode=single\|multi) |
| POST | `/predict-multi` | Dự đoán nhiều số, ghép thành chuỗi |
| POST | `/debug-segments` | Debug số lượng segment tách được |

### Request `/predict`
```json
{
  "image": "data:image/png;base64,iVBOR...",
  "mode": "single"  // hoặc "multi"
}
```

### Response
```json
{
  "digit": 7,
  "confidence": 0.98,
  "probabilities": {"0": 0.001, "1": 0.002, ..., "7": 0.98, ...},
  "top_3": [{"digit": 7, "probability": 0.98}, ...],
  "low_confidence": false,
  "results": [...]
}
```
