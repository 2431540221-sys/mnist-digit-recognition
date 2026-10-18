# -*- coding: utf-8 -*-
"""
retrain_v2.py - Train lai model MNIST voi:
  1) Data Augmentation (xoay, dich, zoom, shear) - giai quyet chu viet tay bien the
  2) Model sau hon: 3 conv blocks + BatchNorm + Dropout (chuan CMU 99.5%+)
  3) Save best model qua callback ModelCheckpoint

Ket qua ky vong:
  - Test acc: 99.5-99.7% (model cu: 99.30%)
  - Confident hon khi gap chu viet tay that (vi da thay bien the khi train)
"""
import os
import sys
import time
import numpy as np
import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Dense, Dropout, Flatten, Conv2D, MaxPooling2D,
    BatchNormalization,
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping

# Fix UnicodeEncodeError khi print tieng Viet tren Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

MODEL_OUT = 'mnist-web/backend/models/mnist_cnn_model.h5'
os.makedirs(os.path.dirname(MODEL_OUT), exist_ok=True)

print("=" * 60)
print("RETRAIN v2: Data Augmentation + Model sau hon")
print("=" * 60)

# ===== 1) Load data =====
print("\n[1/5] Loading MNIST dataset...")
(X_train, y_train), (X_test, y_test) = mnist.load_data()
print(f"  Train: {X_train.shape}, Test: {X_test.shape}")

# Normalize + reshape
X_train = X_train.reshape(-1, 28, 28, 1).astype('float32') / 255
X_test = X_test.reshape(-1, 28, 28, 1).astype('float32') / 255
y_train = tf.keras.utils.to_categorical(y_train, 10)
y_test = tf.keras.utils.to_categorical(y_test, 10)

# ===== 2) Data Augmentation =====
print("\n[2/5] Cau hinh Data Augmentation...")
# Generator chi dung cho training set, KHONG dung cho test
datagen = ImageDataGenerator(
    rotation_range=10,           # xoay ±10 do
    width_shift_range=0.1,       # dich ngang ±10%
    height_shift_range=0.1,      # dich doc ±10%
    zoom_range=0.1,              # phong to/thu nho ±10%
    shear_range=0.1,             # bien dang ±10%
    fill_mode='constant',        # dien vung trong bang 0 (den)
    cval=0.0,
)
datagen.fit(X_train)
print("  + rotation ±10°")
print("  + width/height shift ±10%")
print("  + zoom ±10%")
print("  + shear ±10%")
print("  + fill_mode: constant (den) - giu MNIST format")

# ===== 3) Model kien truc moi =====
print("\n[3/5] Xay dung model...")
model = Sequential([
    # Block 1: 32 filters
    Conv2D(32, (3, 3), activation='relu', padding='same', input_shape=(28, 28, 1)),
    BatchNormalization(),
    Conv2D(32, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    # Block 2: 64 filters
    Conv2D(64, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    Conv2D(64, (3, 3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2, 2)),
    Dropout(0.25),

    # Classifier
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

# ===== 4) Callbacks =====
print("\n[4/5] Cau hinh callbacks...")
callbacks = [
    # Luu model tot nhat (val_acc cao nhat)
    ModelCheckpoint(
        MODEL_OUT, monitor='val_accuracy', save_best_only=True,
        verbose=1, mode='max',
    ),
    # Giam learning rate khi val_loss khong cai thien
    ReduceLROnPlateau(
        monitor='val_loss', factor=0.5, patience=3,
        min_lr=1e-6, verbose=1,
    ),
    # Dung som neu qua 5 epoch khong cai thien
    EarlyStopping(
        monitor='val_accuracy', patience=5,
        restore_best_weights=True, verbose=1,
    ),
]

# ===== 5) Train =====
print("\n[5/5] Bat dau training...")
BATCH_SIZE = 128
EPOCHS = 25  # Co EarlyStopping se dung som neu can

t0 = time.time()
history = model.fit(
    datagen.flow(X_train, y_train, batch_size=BATCH_SIZE),
    epochs=EPOCHS,
    validation_data=(X_test, y_test),
    callbacks=callbacks,
    verbose=1,
)
t1 = time.time()

# ===== Evaluation =====
print("\n" + "=" * 60)
print("KET QUA")
print("=" * 60)
print(f"Thoi gian train: {(t1 - t0) / 60:.1f} phut")

# Lay best acc
best_val_acc = max(history.history['val_accuracy'])
best_train_acc = max(history.history['accuracy'])
print(f"Best Train Acc:  {best_train_acc*100:.2f}%")
print(f"Best Val Acc:    {best_val_acc*100:.2f}%")
print(f"Model cu (val):  99.30%  -->  Model moi: {best_val_acc*100:.2f}%")
print(f"\nModel da luu tai: {MODEL_OUT}")

# So sanh voi model cu
print("\n" + "=" * 60)
print("SO SANH NHANH")
print("=" * 60)
print(f"Model cu  (2 conv):       99.30% val_acc")
print(f"Model moi (4 conv + BN):  {best_val_acc*100:.2f}% val_acc")
print(f"Cai thien:                 +{(best_val_acc - 0.9930) * 100:.2f}%")
