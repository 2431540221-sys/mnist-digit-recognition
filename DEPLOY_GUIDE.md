# Hướng dẫn chạy dự án MNIST Digit Recognition

> Hướng dẫn này gồm 2 phần:
> - **Phần A**: Deploy lên Render (online, miễn phí) ← khuyến nghị
> - **Phần B**: Chạy local (trên máy của bạn)

---

## Phần A — Deploy lên Render (1 cú click, free)

Repo này đã có sẵn file `render.yaml` ở thư mục gốc → Render Blueprint sẽ tự động đọc và tạo 2 service (backend Flask + frontend Vue).

### Bước 1: Chuẩn bị GitHub repo
- Đảm bảo repo `mnist-digit-recognition` đã push lên GitHub (đã xong ✓)
- File `render.yaml` đã có ở root repo (đã có ✓)

### Bước 2: Vào Render
1. Mở https://dashboard.render.com
2. Đăng ký/đăng nhập bằng **GitHub** (bắt buộc dùng account chứa repo mnist-digit-recognition)
3. Nếu repo nằm ở GitHub account khác → vào https://github.com/settings/installations, tìm "Render", click "Configure", chọn "All repositories" hoặc chỉ chọn repo mnist-digit-recognition

### Bước 3: Tạo Blueprint
1. Click **"New +"** → **"Blueprint"**
2. Chọn repo **`mnist-digit-recognition`**
3. Click **"Apply"**
4. Đợi 5–10 phút để build xong cả backend + frontend

### Bước 4: Lấy URL và kiểm tra
- **Backend URL**: `https://mnist-backend.onrender.com` (Render tự tạo)
- **Frontend URL**: `https://mnist-frontend.onrender.com`
- Mở frontend URL → vẽ số → backend sẽ trả về kết quả

### Bước 5 (tùy chọn): Đổi tên service
- Vào từng service trên Render → Settings → Name → đổi nếu muốn

### Lưu ý
- **Free plan**: service sẽ "ngủ" sau 15 phút không có request. Request đầu tiên sau khi ngủ sẽ mất ~30s để wake up
- **CORS**: code đã config whitelist `FRONTEND_URL` env (mặc định cho phép tất cả nếu không set)

---

## Phần B — Chạy local trên máy

### Yêu cầu
- Python 3.10+ (đã test với 3.11.9)
- Node.js 18+ (đã test với 20.x)
- pip, npm

### Bước 1: Clone repo (hoặc mở thư mục đã có)
```bash
cd d:\XLA\mnist-digit-recognition
```

### Bước 2: Chạy backend (Flask + TensorFlow)
```bash
cd mnist-web\backend
pip install -r requirements.txt
python app.py
```
- Mặc định chạy ở `http://localhost:5000`
- Test nhanh: mở `http://localhost:5000/health` → trả về `{"status": "ok"}`

### Bước 3: Chạy frontend (Vue + Vite)
Mở terminal mới:
```bash
cd mnist-web\frontend
npm install
npm run dev
```
- Mặc định chạy ở `http://localhost:5173`
- Vite tự proxy `/api` → `http://localhost:5000`, nên frontend gọi `/api/predict` sẽ tới backend

### Bước 4: Dùng thử
- Mở `http://localhost:5173` trong browser
- Vẽ số trên canvas HOẶC upload ảnh
- Click "Dự đoán" → backend trả về số dự đoán + confidence

### Bước 5 (tùy chọn): Build frontend cho production
```bash
cd mnist-web\frontend
npm run build
# Output ở dist/
```

### Bước 6 (tùy chọn): Test model trực tiếp bằng Python
```bash
cd d:\XLA\mnist-digit-recognition
pip install -r mnist-web\backend\requirements.txt
python predict_own_image_v2.py
```
- Sửa đường dẫn ảnh trong file nếu cần

---

## File quan trọng trong dự án

| File | Vai trò |
|------|---------|
| `mnist-web/backend/app.py` | Flask API (routes /predict, /health, /debug-segments) |
| `mnist-web/backend/preprocessing.py` | Tiền xử lý ảnh + segment nhiều số |
| `mnist-web/backend/models/mnist_cnn_model.h5` | Model CNN đã train (Keras) |
| `mnist-web/backend/requirements.txt` | Python deps |
| `mnist-web/frontend/src/App.vue` | UI chính (Vue 3) |
| `mnist-web/frontend/vite.config.js` | Vite config (proxy + inject API_BASE) |
| `render.yaml` | Render Blueprint (2 services) |
| `handwritten-digit-recognition.ipynb` | Notebook gốc dùng để train model |

---

## Troubleshooting

### Backend không load được model
- Đảm bảo file `mnist_cnn_model.h5` tồn tại trong `mnist-web/backend/models/`
- Kiểm tra version TensorFlow (`pip show tensorflow`)

### Frontend gọi API bị CORS error
- Local: dùng proxy của Vite (`/api`) — không cần CORS
- Production: set `FRONTEND_URL` env var trên Render = URL frontend

### Render free plan chậm lần đầu
- Bình thường, service ngủ sau 15 phút idle → request đầu tiên mất ~30s

### Model accuracy kém
- Model gốc train 5 epochs, accuracy ~99% trên test set
- Nếu ảnh thật (viết tay ngoài đời) bị sai nhiều → cần train thêm với data augmentation
