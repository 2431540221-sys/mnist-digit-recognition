# 🚀 Cách 1: Vercel (Frontend) + Render (Backend) — MIỄN PHÍ

## Bước 1: Push code lên GitHub
```bash
cd D:\XLA\mnist-digit-recognition
git init          # nếu chưa có
git add .
git commit -m "deploy setup"
git branch -M main
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

## Bước 2: Deploy Backend lên Render
1. Vào https://render.com → Sign up bằng GitHub
2. **New** → **Web Service** → chọn repo
3. Cấu hình:
   - **Root Directory:** `mnist-web/backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
   - **Instance Type:** `Free`
4. **Environment Variables:**
   - `PYTHON_VERSION` = `3.11.0`
5. **Advanced:** Thêm `models/` vào repo (cần cho h5 file ~1-5MB)
6. Nhấn **Create Web Service** → đợi 5-10 phút
7. Copy URL: `https://mnist-api-xxx.onrender.com`

## Bước 3: Deploy Frontend lên Vercel
1. Vào https://vercel.com → Sign up bằng GitHub
2. **Add New...** → **Project** → chọn repo
3. Cấu hình:
   - **Root Directory:** `mnist-web/frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. **Environment Variables:**
   - `VITE_API_BASE_URL` = `https://mnist-api-xxx.onrender.com`
5. Nhấn **Deploy** → đợi 1-2 phút
6. Xong! Có URL: `https://mnist-app.vercel.app`

## Bước 4: Test
Mở URL Vercel trên trình duyệt, vẽ 1 số rồi bấm Dự đoán.
Lưu ý: Render free sẽ "ngủ" sau 15 phút không có request, request đầu tiên có thể chậm 30-60s.

## CORS (nếu cần)
Backend đã có `flask-cors` cho phép tất cả origin. Nếu bị chặn:
```python
CORS(app, origins=["https://mnist-app.vercel.app"])
```
