# Nhận diện chữ số viết tay (MNIST) + Web demo (Vue + Flask)

Project gồm 3 phần:
- **`mnist_train.py`** — train model CNN nhận diện chữ số viết tay (dataset MNIST)
- **`mnist-web/backend/`** — API Python (Flask) load model đã train, xử lý ảnh bằng OpenCV, trả kết quả dự đoán
- **`mnist-web/frontend/`** — giao diện web (Vue.js) cho người dùng vẽ chữ số và xem kết quả

---

## Yêu cầu trước khi bắt đầu

| Phần mềm | Phiên bản yêu cầu | Vì sao |
|---|---|---|
| Python | **3.9 – 3.12** (KHÔNG dùng 3.13 trở lên) | TensorFlow chưa hỗ trợ Python 3.13+ |
| Node.js | Bản LTS mới nhất | Cần để chạy frontend Vue |
| PyCharm | Bất kỳ bản nào | Không ảnh hưởng, chỉ là công cụ code |

---

## Bước 1: Clone project về máy

1. Mở PyCharm → **Get from VCS**
2. Dán link repo GitHub, chọn nơi lưu → **Clone**

---

## Bước 2: Cài Python đúng phiên bản (nếu máy chưa có 3.9–3.12)

1. Kiểm tra phiên bản Python đang có:
   ```bash
   python --version
   ```
2. Nếu là Python 3.13 trở lên (hoặc chưa cài Python), tải bản 3.12 tại:
   👉 https://www.python.org/downloads/release/python-3120/
   → chọn **Windows installer (64-bit)**
3. Khi cài, **nhớ tick vào ô "Add python.exe to PATH"** ở màn hình đầu tiên trước khi bấm Install.

---

## Bước 3: Tạo virtual environment với đúng Python 3.12

1. Trong PyCharm: **File → Settings → Project → Python Interpreter**
2. Bấm bánh răng ⚙️ (góc trên phải) → **Add Interpreter → Add Local Interpreter**
3. Chọn tab **Virtualenv Environment** → **New**
4. Ở ô **Base interpreter**, chọn đường dẫn tới Python 3.12 vừa cài
5. Bấm **OK**

---

## Bước 4: Cài thư viện Python cho backend

Mở **Terminal** trong PyCharm (đảm bảo thấy tiền tố venv, ví dụ `(.venv)`, ở đầu dòng lệnh):

```bash
cd mnist-web\backend
pip install -r requirements.txt
```

Thư viện sẽ được cài: `flask`, `flask-cors`, `tensorflow`, `pillow`, `numpy`, `opencv-python`.

Kiểm tra cài đặt thành công:
```bash
python -c "import tensorflow as tf; import cv2; print('TF:', tf.__version__); print('OpenCV:', cv2.__version__)"
```
Nếu in ra 2 dòng số phiên bản là ổn.

---

## Bước 5: Cài Node.js cho frontend

1. Tải bản **LTS** tại: 👉 https://nodejs.org
2. Cài đặt theo mặc định (Next liên tục)
3. **Đóng và mở lại PyCharm** (quan trọng — để PATH mới được nhận)
4. Kiểm tra:
   ```bash
   node --version
   npm --version
   ```

---

## Bước 6: Cài thư viện frontend (Vue.js)

```bash
cd mnist-web\frontend
npm install
```

Đợi 1-2 phút để npm tải các thư viện (Vue, Vite...) về.

---

## Bước 7: Chuẩn bị file model đã train

Backend cần file model tại đường dẫn:
```
mnist-web\backend\models\mnist_cnn_model.h5
```

**Cách 1 — Nếu file này đã có sẵn trong repo (do không bị .gitignore loại trừ):**
Không cần làm gì thêm, bỏ qua bước này.

**Cách 2 — Nếu chưa có (do model quá nặng, không push lên Git):**
Cần train lại từ đầu bằng lệnh:
```bash
cd ..\..
python mnist_train.py
```
Sau khi train xong (khoảng 5-10 phút), model sẽ lưu vào `models\mnist_cnn_model.h5` ở thư mục gốc. Copy thư mục `models` đó vào trong `mnist-web\backend\`.

---

## Bước 8: Chạy project (cần 2 Terminal chạy song song)

**Terminal 1 — chạy Backend:**
```bash
cd mnist-web\backend
python app.py
```
Thấy dòng `Model đã load thành công` và `Running on http://127.0.0.1:5000` là backend đã chạy ổn.

**Terminal 2 (mở tab mới, đừng đóng Terminal 1) — chạy Frontend:**
```bash
cd mnist-web\frontend
npm run dev
```
Terminal in ra link, ví dụ `http://localhost:5173/`.

---

## Bước 9: Mở web và thử

Mở trình duyệt (Chrome/Edge), truy cập link ở Bước 8 (thường là `http://localhost:5173/`).

- Vẽ 1 hoặc nhiều chữ số vào khung
- Bấm **Dự đoán**
- Xem kết quả model đoán được

**Lưu ý khi vẽ để đoán chính xác:**
- Viết cách nhau rõ ràng, đừng để 2 số dính/chạm vào nhau
- Viết nét đậm, đơn giản, tránh bay bướm hay thêm nét thừa
- Viết chữ số đủ to, chiếm phần lớn chiều cao khung vẽ
- Canh chữ số nằm giữa dòng, không quá sát mép trên/dưới

---

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Cách sửa |
|---|---|---|
| `ModuleNotFoundError: No module named 'tensorflow'` | Chưa cài đúng venv hoặc quên `pip install` | Chạy lại Bước 4, đảm bảo đang ở đúng venv |
| `pip install tensorflow` báo "No matching distribution" | Python quá mới (3.13+) | Làm lại Bước 2–3 với Python 3.12 |
| `node : is not recognized` | Chưa cài Node.js hoặc chưa mở lại PyCharm sau khi cài | Làm lại Bước 5, nhớ mở Terminal MỚI |
| `Cannot find path 'frontend'` khi chạy `cd frontend` | Đang đứng sai thư mục | Kiểm tra bằng `dir`, đảm bảo `cd` đúng đường dẫn `mnist-web\frontend` |
| Web báo "Không kết nối được backend" | Backend (`python app.py`) chưa chạy hoặc đã tắt | Kiểm tra Terminal 1 vẫn đang chạy, chưa bị đóng |
| Backend báo không tìm thấy file `.h5` | Chưa copy/train model đúng chỗ | Làm lại Bước 7 |
