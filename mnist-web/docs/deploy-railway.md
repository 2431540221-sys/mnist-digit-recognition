# 🚂 Cách 2: Railway.app — 1 service, dễ nhất

Railway cho free $5 credit/tháng, đủ chạy 1 web service nhỏ.

## Bước 1: Push code lên GitHub
```bash
git add .
git commit -m "railway setup"
git push
```

## Bước 2: Deploy trên Railway
1. Vào https://railway.app → Sign up bằng GitHub
2. **New Project** → **Deploy from GitHub repo** → chọn repo
3. Railway tự detect Python qua `Procfile` / `railway.json`
4. **Variables** tab → thêm:
   - `PORT` (Railway tự set, không cần đụng)
5. **Settings** → **Root Directory:** `mnist-web`
6. **Generate Domain** → copy URL: `https://xxx.up.railway.app`
7. Đợi build 5-10 phút

## Bước 3: Test
Mở URL → vẽ số → dự đoán.
- `/` → Vue SPA (Vite build serve qua static)
- `/predict` → Flask API

**Lưu ý:** Railway mặc định KHÔNG serve Vue build, mà chỉ chạy Flask.
Cần custom build. Tôi sẽ tạo sẵn file `backend/serve_frontend.py` để Flask serve Vue dist:

Xem file: `backend/serve_frontend.py`
