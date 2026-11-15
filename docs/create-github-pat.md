# Cách tạo Personal Access Token (PAT) trên GitHub

Token cho phép mình merge PR qua API mà không cần GitHub CLI.

## Bước 1: Mở trang tạo token
Truy cập: **https://github.com/settings/tokens/new**

(hoặc: GitHub → avatar góc phải → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token** → **Generate new token (classic)**)

## Bước 2: Cấu hình
- **Note (tên token):** `deploy-mnist-railway`
- **Expiration:** `7 days` (hoặc `No expiration` nếu bạn muốn)
- **Scopes:** tick các mục sau:
  - ✅ **`repo`** (Full control of private repositories) — QUAN TRỌNG
  - ✅ `workflow` (nếu muốn, không bắt buộc)

## Bước 3: Generate
- Kéo xuống cuối → **Generate token**
- GitHub sẽ hiện token 1 lần duy nhất, dạng: `ghp_xxxxxxxxxxxxxxxxxxxx`

## Bước 4: Gửi token cho mình
**QUAN TRỌNG — BẢO MẬT:**
- Copy token đó → paste vào chat với mình
- Token chỉ dùng 1 lần để merge PR
- Sau khi deploy xong, **vào Settings → Personal access tokens → Delete** token đi
- Token KHÔNG được push lên git, không share cho ai khác

## Sau khi merge xong
Mình sẽ:
1. Merge branch `feat/deploy-configs` vào `main`
2. Verify Dockerfile, Procfile, model .h5 đã có trên main
3. Hướng dẫn bạn deploy Railway với 3 click
