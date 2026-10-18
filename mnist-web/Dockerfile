# Multi-stage build cho MNIST Digit Recognition
# Stage 1: Build Vue frontend
# Stage 2: Setup Python backend + serve tất cả qua Gunicorn

# ============ STAGE 1: Frontend ============
FROM node:20-alpine AS frontend

WORKDIR /app/frontend

# Copy package files trước để tận dụng cache
COPY frontend/package*.json ./
RUN npm ci

# Copy source + build
COPY frontend/ ./
RUN npm run build

# ============ STAGE 2: Backend ============
FROM python:3.11-slim

# Cài deps hệ thống cho OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài Python deps trước để cache
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend (gồm models/ chứa file .h5)
COPY backend/ ./backend/

# Copy frontend build từ stage 1
COPY --from=frontend /app/frontend/dist ./backend/static/

WORKDIR /app/backend

# Port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Chạy production server
CMD ["gunicorn", "serve_frontend:app", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "180"]
