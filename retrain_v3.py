# -*- coding: utf-8 -*-
"""
retrain_v3.py - Huan luyen lai de nhan dien tot hon chu VE TAY / CHUOT.

Khac retrain_v2.py:
  1) Augmentation gan voi net ve that: doi do day net (dilate/erode ngau nhien),
     xoay ±15 do, shear ±0.2, zoom 0.85-1.15, dich ±12%, noise nhe.
  2) Giu nguyen kien truc 17 lop hien tai (model_info/web khong can sua).
  3) Luu ra file MOI (mnist_cnn_model_v3.h5), KHONG ghi de model dang chay.
  4) In bao cao tung chu so + cac cap hay nham (3->5, 7->1, 6->5, ...).

Chay (tu thu muc goc du an):   python retrain_v3.py
Sau khi xem ket qua tot hon, doi ten file v3 thanh mnist_cnn_model.h5 de dung.
"""
import os
import sys
import time
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Dense, Dropout, Flatten, Conv2D, MaxPooling2D, BatchNormalization,
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

MODEL_OUT = 'mnist-web/backend/models/mnist_cnn_model_v3.h5'
os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)
BATCH_SIZE = 128
EPOCHS = 40
rng = np.random.default_rng(42)


# ---------------------------------------------------------------- augmentation
def augment_one(img):
    """img: (28, 28) float32 trong [0, 1] -> anh da bien dang."""
    angle = rng.uniform(-15, 15)
    zoom = rng.uniform(0.85, 1.15)
    shear = rng.uniform(-0.2, 0.2)
    tx, ty = rng.uniform(-3.3, 3.3, size=2)

    c = 14.0
    A = np.array([[1, shear], [0, 1]], dtype=np.float32)
    R = cv2.getRotationMatrix2D((c, c), angle, zoom)[:, :2].astype(np.float32)
    M2 = R @ A
    t = np.array([c, c], dtype=np.float32) - M2 @ np.array([c, c], dtype=np.float32)
    M = np.hstack([M2, (t + [tx, ty]).reshape(2, 1)]).astype(np.float32)
    out = cv2.warpAffine(img, M, (28, 28), flags=cv2.INTER_LINEAR,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=0)

    # doi do day net: 25% day hon, 15% mong hon
    r = rng.random()
    k = np.ones((2, 2), np.uint8)
    if r < 0.25:
        out = cv2.dilate(out, k)
    elif r < 0.40:
        out = cv2.erode(out, k)

    if rng.random() < 0.3:
        out = np.clip(out + rng.normal(0, 0.03, out.shape), 0, 1)
    return out.astype(np.float32)


class AugSeq(tf.keras.utils.Sequence):
    def __init__(self, x, y, batch_size):
        super().__init__()
        self.x, self.y, self.bs = x, y, batch_size
        self.idx = np.arange(len(x))
        rng.shuffle(self.idx)

    def __len__(self):
        return len(self.x) // self.bs

    def __getitem__(self, i):
        ids = self.idx[i * self.bs:(i + 1) * self.bs]
        xb = np.stack([augment_one(self.x[j, :, :, 0]) for j in ids])[..., None]
        return xb, self.y[ids]

    def on_epoch_end(self):
        rng.shuffle(self.idx)


# ----------------------------------------------------------------------- data
print("[1/4] Loading MNIST...")
(X_train, y_train), (X_test, y_test) = mnist.load_data()
X_train = X_train.reshape(-1, 28, 28, 1).astype('float32') / 255
X_test = X_test.reshape(-1, 28, 28, 1).astype('float32') / 255
y_test_int = y_test.copy()
y_train = tf.keras.utils.to_categorical(y_train, 10)
y_test = tf.keras.utils.to_categorical(y_test, 10)

# ---------------------------------------------------------------------- model
print("[2/4] Build model (cung kien truc voi model dang chay)...")
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(28, 28, 1)),
    BatchNormalization(),
    Conv2D(32, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    Dropout(0.25),
    Conv2D(64, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    Conv2D(64, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D((2, 2)),
    Dropout(0.25),
    Flatten(),
    Dense(256, activation='relu'),
    BatchNormalization(),
    Dropout(0.5),
    Dense(10, activation='softmax'),
])
model.compile(loss='categorical_crossentropy', optimizer=Adam(1e-3), metrics=['accuracy'])

callbacks = [
    ModelCheckpoint(MODEL_OUT, monitor='val_accuracy', save_best_only=True, mode='max', verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6, verbose=1),
    EarlyStopping(monitor='val_accuracy', patience=7, restore_best_weights=True, verbose=1),
]

# ---------------------------------------------------------------------- train
print("[3/4] Training...")
t0 = time.time()
model.fit(AugSeq(X_train, y_train, BATCH_SIZE), epochs=EPOCHS,
          validation_data=(X_test, y_test), callbacks=callbacks, verbose=1)
print(f"Thoi gian train: {(time.time() - t0) / 60:.1f} phut")

# ------------------------------------------------------------------- evaluate
print("[4/4] Danh gia tren tap test MNIST + tap test bi bien dang (gia lap nét vẽ)...")
loss, acc = model.evaluate(X_test, y_test, verbose=0)
print(f"Test accuracy (MNIST goc):       {acc * 100:.2f}%")

rng2 = np.random.default_rng(7)
rng_backup, rng = rng, rng2          # seed co dinh cho tap bi bien dang
X_aug = np.stack([augment_one(x[:, :, 0]) for x in X_test])[..., None]
rng = rng_backup
pred = model.predict(X_aug, verbose=0).argmax(1)
print(f"Test accuracy (anh bi bien dang): {(pred == y_test_int).mean() * 100:.2f}%")

print("\nDo chinh xac tung chu so (tren anh bi bien dang):")
for d in range(10):
    m = y_test_int == d
    print(f"  {d}: {(pred[m] == d).mean() * 100:.2f}%")

print("\nCac cap hay nham nhat (that -> doan):")
conf = {}
for t, p in zip(y_test_int, pred):
    if t != p:
        conf[(t, p)] = conf.get((t, p), 0) + 1
for (t, p), n in sorted(conf.items(), key=lambda kv: -kv[1])[:8]:
    print(f"  {t} -> {p}: {n} lan")

print(f"\nModel luu tai: {MODEL_OUT}")
print("Neu tot hon: doi ten thanh mnist_cnn_model.h5 (nho backup file cu).")
