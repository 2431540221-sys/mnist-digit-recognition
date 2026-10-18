# 🐳 Cách 3: Docker — chạy local / VPS / bất kỳ đâu

## A. Chạy local bằng Docker Compose (khuyến nghị)
```bash
cd D:\XLA\mnist-digit-recognition\mnist-web

# Build + chạy
docker compose up -d --build

# Mở trình duyệt
# → http://localhost:5000

# Xem log
docker compose logs -f

# Dừng
docker compose down
```

## B. Build image thủ công
```bash
docker build -t mnist-app .
docker run -p 5000:5000 -v ./backend/models:/app/backend/models mnist-app
```

## C. Deploy lên VPS (DigitalOcean / AWS EC2 / Azure VM)

### Bước 1: SSH vào VPS
```bash
ssh root@your-server-ip
```

### Bước 2: Cài Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### Bước 3: Copy code lên
```bash
# Từ máy local:
scp -r D:\XLA\mnist-digit-recognition\mnist-web root@your-server-ip:/opt/
```

### Bước 4: Chạy
```bash
cd /opt/mnist-web
docker compose up -d --build
```

### Bước 5: Domain + HTTPS (Nginx + Let's Encrypt)
```bash
apt install -y nginx certbot python3-certbot-nginx
```

File `/etc/nginx/sites-available/mnist`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    client_max_body_size 10M;  # upload ảnh

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 180s;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/mnist /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
certbot --nginx -d yourdomain.com
```

Xong! Truy cập `https://yourdomain.com` 🎉

## D. Deploy lên các cloud Docker host

- **Railway:** `railway up` (auto detect Dockerfile)
- **Render:** chọn "Docker" làm runtime
- **Fly.io:** `flyctl launch --dockerfile`
- **Google Cloud Run:** `gcloud run deploy --source .`
- **AWS App Runner:** push image lên ECR, tạo service

## Lưu ý
- File `mnist_cnn_model.h5` (~1-5MB) nên được copy vào image hoặc mount volume
- TensorFlow cần RAM ~300-500MB → chọn instance >= 1GB RAM
- OpenCV cần `libgl1` (đã có trong Dockerfile)
- Cold start ~10-20s (do load model)
