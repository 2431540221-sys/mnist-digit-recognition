import os
import keras
from keras.datasets import mnist
from keras.models import load_model
import numpy as np
import matplotlib.pyplot as plt

# Tạo thư mục lưu kết quả nếu chưa có
os.makedirs('outputs', exist_ok=True)

# 1. Load model đã train
model = load_model('models/mnist_cnn_model.h5')
print("Đã load model thành công")

# 2. Load tập test MNIST
(_, _), (X_test, y_test) = mnist.load_data()

# Chuẩn hóa giống lúc train
X_test_norm = X_test.reshape(X_test.shape[0], 28, 28, 1).astype('float32') / 255

# 3. Chọn ngẫu nhiên 10 ảnh trong tập test để thử
num_samples = 10
indices = np.random.choice(len(X_test), num_samples, replace=False)

# 4. Dự đoán
predictions = model.predict(X_test_norm[indices])
predicted_labels = np.argmax(predictions, axis=1)

# 5. Hiển thị kết quả
fig, axes = plt.subplots(2, 5, figsize=(12, 5))
for i, idx in enumerate(indices):
    ax = axes[i // 5, i % 5]
    ax.imshow(X_test[idx], cmap='gray')
    true_label = y_test[idx]
    pred_label = predicted_labels[i]
    color = 'green' if true_label == pred_label else 'red'
    ax.set_title(f"Thật: {true_label} | Đoán: {pred_label}", color=color)
    ax.axis('off')

plt.tight_layout()
plt.savefig('outputs/predictions_result.png')
print("Đã lưu kết quả vào outputs/predictions_result.png")
plt.show()

# In thêm chi tiết ra console
print("\nChi tiết:")
for i, idx in enumerate(indices):
    status = "ĐÚNG" if y_test[idx] == predicted_labels[i] else "SAI"
    print(f"Ảnh {idx}: Nhãn thật = {y_test[idx]}, Model đoán = {predicted_labels[i]} -> {status}")
