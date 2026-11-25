# -*- coding: utf-8 -*-
"""
Module huấn luyện mô hình CNN nhận diện chữ số viết tay MNIST:
  1) Data Augmentation (xoay, dịch chuyển, zoom, shear với constant zero-padding).
  2) Kiến trúc CNN chuẩn sâu: 4 Conv2D + BatchNormalization + Dropout + Dense.
  3) Callbacks: ReduceLROnPlateau, EarlyStopping, ModelCheckpoint (lưu trọng số tốt nhất).
  4) Tự động lưu mô hình vào cả thư mục gốc và thư mục backend của web.
"""

import os
import sys
import shutil
import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping

# Fix hiển thị tiếng Việt trên Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

MODEL_PATH_ROOT = 'models/mnist_cnn_model.h5'
MODEL_PATH_BACKEND = 'mnist-web/backend/models/mnist_cnn_model.h5'

os.makedirs('models', exist_ok=True)
os.makedirs('mnist-web/backend/models', exist_ok=True)

# 1. Tải và chuẩn bị dữ liệu MNIST
print("=" * 60)
print("[1/5] Đang nạp tập dữ liệu MNIST...")
(X_train, y_train), (X_test, y_test) = mnist.load_data()
print(f"  Train: {X_train.shape}, Test: {X_test.shape}")

# Chuẩn hóa về [0, 1] và reshape (28, 28, 1)
X_train = X_train.reshape(-1, 28, 28, 1).astype('float32') / 255.0
X_test = X_test.reshape(-1, 28, 28, 1).astype('float32') / 255.0
y_train = tf.keras.utils.to_categorical(y_train, 10)
y_test = tf.keras.utils.to_categorical(y_test, 10)

# 2. Cấu hình Data Augmentation
print("\n[2/5] Cấu hình Data Augmentation...")
datagen = ImageDataGenerator(
    rotation_range=12,          # Xoay ngẫu nhiên ±12 độ
    width_shift_range=0.1,      # Dịch ngang ±10%
    height_shift_range=0.1,     # Dịch dọc ±10%
    zoom_range=0.1,             # Phóng to/thu nhỏ ±10%
    shear_range=0.1,            # Biến dạng nghiêng ±10%
    fill_mode='constant',       # Điền viền bằng màu đen (0.0) đúng chuẩn MNIST
    cval=0.0,
)
datagen.fit(X_train)

# 3. Xây dựng kiến trúc mô hình CNN
print("\n[3/5] Khởi tạo kiến trúc mô hình CNN...")
model = Sequential([
    # Block 1
    Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(28, 28, 1)),
    BatchNormalization(),
    Conv2D(32, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    # Block 2
    Conv2D(64, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    Conv2D(64, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    # Dense Classifier
    Flatten(),
    Dense(256, activation='relu'),
    BatchNormalization(),
    Dropout(0.5),
    Dense(10, activation='softmax'),
])

model.compile(
    loss=tf.keras.losses.categorical_crossentropy,
    optimizer=Adam(learning_rate=0.001),
    metrics=['accuracy'],
)
model.summary()

# 4. Cấu hình Callbacks
print("\n[4/5] Thiết lập Callbacks...")
callbacks = [
    # Lưu model tốt nhất (dựa trên val_accuracy)
    ModelCheckpoint(
        MODEL_PATH_ROOT,
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1,
        mode='max',
    ),
    # Giảm learning rate khi val_loss không cải thiện sau 2 epochs
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=2,
        min_lr=1e-6,
        verbose=1,
    ),
    # Dừng sớm nếu qua 5 epochs val_accuracy không tăng
    EarlyStopping(
        monitor='val_accuracy',
        patience=5,
        restore_best_weights=True,
        verbose=1,
    ),
]

# 5. Huấn luyện mô hình
BATCH_SIZE = 128
EPOCHS = 25

print("\n[5/5] Bắt đầu quá trình huấn luyện...")
history = model.fit(
    datagen.flow(X_train, y_train, batch_size=BATCH_SIZE),
    epochs=EPOCHS,
    validation_data=(X_test, y_test),
    callbacks=callbacks,
    verbose=1,
)

# Đánh giá lại kết quả cuối cùng
score = model.evaluate(X_test, y_test, verbose=0)
print("\n" + "=" * 60)
print(f"KẾT QUẢ HUẤN LUYỆN:")
print(f"  Test Loss:     {score[0]:.4f}")
print(f"  Test Accuracy: {score[1] * 100:.2f}%")
print("=" * 60)

# Đồng bộ mô hình tốt nhất sang backend
if os.path.exists(MODEL_PATH_ROOT):
    shutil.copyfile(MODEL_PATH_ROOT, MODEL_PATH_BACKEND)
    print(f"Đã lưu mô hình tốt nhất vào:")
    print(f"  - {MODEL_PATH_ROOT}")
    print(f"  - {MODEL_PATH_BACKEND}")

# Hình 3.4: vẽ đồ thị accuracy / loss theo epoch từ history
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

os.makedirs('report_figures', exist_ok=True)
h = history.history
with open('report_figures/history.json', 'w', encoding='utf-8') as f:
    json.dump({k: [float(x) for x in v] for k, v in h.items()}, f, indent=2)

epochs = range(1, len(h['accuracy']) + 1)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
ax1.plot(epochs, h['accuracy'], label='accuracy (train)')
ax1.plot(epochs, h['val_accuracy'], label='val_accuracy')
ax1.set_xlabel('Epoch'); ax1.set_ylabel('Accuracy'); ax1.legend(); ax1.grid(alpha=0.3)
ax2.plot(epochs, h['loss'], label='loss (train)')
ax2.plot(epochs, h['val_loss'], label='val_loss')
ax2.set_xlabel('Epoch'); ax2.set_ylabel('Loss'); ax2.legend(); ax2.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('report_figures/hinh_3_4_accuracy_loss.png', dpi=200)
best = int(np.argmax(h['val_accuracy'])) + 1
print(f"Số epoch đã chạy: {len(h['accuracy'])}; epoch tốt nhất: {best}; "
      f"val_accuracy tốt nhất: {max(h['val_accuracy']) * 100:.2f}%; "
      f"val_loss tương ứng: {h['val_loss'][best - 1]:.4f}")
print("Đã lưu hình 3.4 vào report_figures/hinh_3_4_accuracy_loss.png")