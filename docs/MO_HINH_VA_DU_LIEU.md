# Trả lời các câu hỏi về dữ liệu và mô hình CNN

(Số liệu đọc từ `mnist_train.py` và từ model `mnist_cnn_model.h5`. Trên web, phần cuối trang hiển thị cùng thông tin, lấy từ `GET /model-info`.)

## 1. Bước hiển thị lỗi có đi qua mô hình và trả về lỗi không?
Tùy loại lỗi. Backend giờ trả thêm `error_stage` và `passed_model`, web hiển thị rõ:

| Bước báo lỗi | Ví dụ | Đã qua mô hình CNN? |
|---|---|---|
| `input` – dữ liệu vào | thiếu ảnh, base64/JSON hỏng | Chưa |
| `preprocess` – tiền xử lý | ảnh trống, nét vẽ phủ kín khung, không tách được chữ số | Chưa |
| `model` – mô hình CNN | mô hình dự đoán nhưng độ tin cậy < 60% (mode 1 số) hoặc trung bình < 65% (mode nhiều số) | **Rồi** (kèm độ tin cậy) |
| `network` (chỉ ở frontend) | backend không chạy | Chưa |

## 2. Chỉnh layout sáng
Toàn bộ giao diện đã chuyển sang nền sáng. Riêng khung vẽ giữ nền đen vì mô hình MNIST cần chữ trắng trên nền đen.

## 3. Dữ liệu lấy từ đâu (hình ảnh hay text)?
Bộ **MNIST**, nạp bằng `tensorflow.keras.datasets.mnist` (tự tải `mnist.npz`). Dữ liệu là **hình ảnh** xám 28×28 px (0–255) kèm nhãn số 0–9, không phải text. Chia 255 để về [0, 1].

## 4. Bao nhiêu mẫu, chia validation bao nhiêu %, bao nhiêu lớp?
- Tổng 70.000 mẫu: train 60.000 (85,71%), validation 10.000 (14,29%).
- Lưu ý: code hiện dùng 10.000 mẫu test chuẩn của MNIST làm validation (không có tập test riêng).
- Số lớp (class): 10 (chữ số 0–9).

## 5. Đầu vào
Ảnh một chữ số viết tay 28×28×1. Đầu ra là vector 10 xác suất (softmax), mỗi phần tử ứng với một chữ số 0–9.

## 6. Mỗi lớp dùng tích chập, hàm kích hoạt nào?
Toàn bộ tích chập là kernel 3×3, stride 1, padding `same`; hàm kích hoạt ReLU, riêng lớp cuối softmax.

## 7. CNN có bao nhiêu lớp, cấu hình thế nào?
17 lớp Keras (6 lớp có trọng số chính: 4 Conv2D + 2 Dense), tổng 872.426 tham số.

| # | Lớp | Cấu hình | Đầu ra | Tham số | Kích hoạt |
|---|---|---|---|---|---|
| 1 | Conv2D | 32 bộ lọc 3×3 | 28×28×32 | 320 | ReLU |
| 2 | BatchNorm | | 28×28×32 | 128 | |
| 3 | Conv2D | 32 bộ lọc 3×3 | 28×28×32 | 9.248 | ReLU |
| 4 | BatchNorm | | 28×28×32 | 128 | |
| 5 | MaxPooling | 2×2 | 14×14×32 | 0 | |
| 6 | Dropout | 0,25 | 14×14×32 | 0 | |
| 7 | Conv2D | 64 bộ lọc 3×3 | 14×14×64 | 18.496 | ReLU |
| 8 | BatchNorm | | 14×14×64 | 256 | |
| 9 | Conv2D | 64 bộ lọc 3×3 | 14×14×64 | 36.928 | ReLU |
| 10 | BatchNorm | | 14×14×64 | 256 | |
| 11 | MaxPooling | 2×2 | 7×7×64 | 0 | |
| 12 | Dropout | 0,25 | 7×7×64 | 0 | |
| 13 | Flatten | | 3136 | 0 | |
| 14 | Dense | 256 nơ-ron | 256 | 803.072 | ReLU |
| 15 | BatchNorm | | 256 | 1.024 | |
| 16 | Dropout | 0,5 | 256 | 0 | |
| 17 | Dense | 10 nơ-ron | 10 | 2.570 | Softmax |

Huấn luyện: Adam (lr 0,001), categorical_crossentropy, batch 128, tối đa 25 epoch, augmentation (xoay ±12°, dịch/zoom/shear ±10%), callbacks ModelCheckpoint, ReduceLROnPlateau, EarlyStopping.
