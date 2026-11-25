# -*- coding: utf-8 -*-
"""
Tạo số liệu + hình cho báo cáo (các chỗ tô vàng).

Chạy từ thư mục gốc project (cạnh mnist_train.py):
  python make_report_figures.py eval
      -> Bảng 3.6 (accuracy/loss), bảng precision/recall/F1 từng chữ số,
         Hình 3.5 (ma trận nhầm lẫn), Hình 3.6 (ảnh dự đoán sai), 3 cặp nhầm nhiều nhất
  python make_report_figures.py preprocess duong_dan_anh.png
      -> Hình 3.7 (các bước tiền xử lý), Hình 3.8 (so sánh 1 chữ số vs nhiều chữ số)

Kết quả lưu trong thư mục report_figures/
Cần: pip install matplotlib seaborn scikit-learn (đã có TensorFlow, OpenCV)
"""
import os
import sys

MODEL_PATH = 'mnist-web/backend/models/mnist_cnn_model.h5'
OUT = 'report_figures'
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join('mnist-web', 'backend'))

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def run_eval():
    import seaborn as sns
    from tensorflow.keras.datasets import mnist
    from tensorflow.keras.models import load_model
    from sklearn.metrics import confusion_matrix, classification_report

    (_, _), (X_test, y_test) = mnist.load_data()
    X = X_test.reshape(-1, 28, 28, 1).astype('float32') / 255.0
    model = load_model(MODEL_PATH)

    loss, acc = model.evaluate(X, tf_onehot(y_test), verbose=0)
    print('=' * 60)
    print('BẢNG 3.6 — Mô hình của đề tài (điền vào 2 ô [ĐIỀN])')
    print(f'  Accuracy: {acc * 100:.2f}%   Loss: {loss:.4f}')

    pred = np.argmax(model.predict(X, verbose=0), axis=1)
    print('\nBẢNG PRECISION / RECALL / F1 TỪNG CHỮ SỐ')
    print(classification_report(y_test, pred, digits=4))
    with open(os.path.join(OUT, 'classification_report.txt'), 'w', encoding='utf-8') as f:
        f.write(f'Accuracy: {acc * 100:.2f}%  Loss: {loss:.4f}\n\n')
        f.write(classification_report(y_test, pred, digits=4))

    # Hình 3.5
    cm = confusion_matrix(y_test, pred)
    plt.figure(figsize=(7, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=range(10), yticklabels=range(10))
    plt.xlabel('Nhãn dự đoán'); plt.ylabel('Nhãn thật')
    plt.title('Ma trận nhầm lẫn trên tập kiểm tra MNIST')
    plt.tight_layout(); plt.savefig(os.path.join(OUT, 'hinh_3_5_confusion_matrix.png'), dpi=200)
    plt.close()

    # 3 cặp nhầm nhiều nhất (cho phần Nhận xét)
    off = cm.copy(); np.fill_diagonal(off, 0)
    idx = np.dstack(np.unravel_index(np.argsort(off.ravel())[::-1], off.shape))[0][:3]
    print('3 CẶP NHẦM NHIỀU NHẤT (thật -> đoán: số ảnh):')
    for t, p in idx:
        print(f'  {t} -> {p}: {off[t, p]}')

    # Hình 3.6
    wrong = np.where(pred != y_test)[0]
    print(f'\nSố ảnh dự đoán sai: {len(wrong)} / {len(y_test)}')
    pick = wrong[:12]
    fig, axes = plt.subplots(2, 6, figsize=(10, 4.4))
    for ax, i in zip(axes.ravel(), pick):
        ax.imshow(X_test[i], cmap='gray'); ax.axis('off')
        ax.set_title(f'Thật: {y_test[i]} | Đoán: {pred[i]}', fontsize=9)
    for ax in axes.ravel()[len(pick):]:
        ax.axis('off')
    plt.tight_layout(); plt.savefig(os.path.join(OUT, 'hinh_3_6_misclassified.png'), dpi=200)
    plt.close()
    print(f'\nĐã lưu hình vào thư mục {OUT}/')


def tf_onehot(y):
    import tensorflow as tf
    return tf.keras.utils.to_categorical(y, 10)


def run_preprocess(path):
    import cv2
    from PIL import Image
    import preprocessing as P

    img = Image.open(path)
    gray, _ = P._pil_to_cv2_gray(img)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    binary, _ = P._binarize(img, dilate_iter=0)      # sau nhị phân hóa
    dilated, _ = P._binarize(img, dilate_iter=1)     # sau giãn nở

    digits, err = P.segment_multi_digits(img)
    # vẽ hộp bao
    boxed = cv2.cvtColor(dilated, cv2.COLOR_GRAY2BGR)
    cnts, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        if cv2.contourArea(c) >= P.MIN_AREA:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(boxed, (x, y), (x + w, y + h), (0, 255, 0), 2)

    steps = [('Ảnh gốc', np.array(img.convert('RGB'))), ('Ảnh xám', gray),
             ('Lọc Gaussian', blurred), ('Nhị phân hóa', binary),
             ('Giãn nở', dilated), ('Hộp bao', cv2.cvtColor(boxed, cv2.COLOR_BGR2RGB))]
    n = len(steps) + max(len(digits), 1)
    fig, axes = plt.subplots(1, n, figsize=(2.2 * n, 2.8))
    for ax, (title, im) in zip(axes, steps):
        ax.imshow(im, cmap='gray' if im.ndim == 2 else None); ax.set_title(title, fontsize=8); ax.axis('off')
    for k, ax in enumerate(axes[len(steps):]):
        if k < len(digits):
            ax.imshow(digits[k].reshape(28, 28), cmap='gray'); ax.set_title(f'28×28 #{k + 1}', fontsize=8)
        ax.axis('off')
    plt.tight_layout(); plt.savefig(os.path.join(OUT, 'hinh_3_7_preprocess.png'), dpi=200); plt.close()

    # Hình 3.8
    def draw(dil, gap, title, ax):
        b, _ = P._binarize(img, dilate_iter=dil)
        cs, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        raw = [cv2.boundingRect(c) for c in cs if cv2.contourArea(c) >= P.MIN_AREA]
        merged = P._merge_close_boxes(raw, merge_gap=gap) if raw else []
        vis = cv2.cvtColor(b, cv2.COLOR_GRAY2RGB)
        for x, y, w, h in merged:
            cv2.rectangle(vis, (x, y), (x + w, y + h), (255, 0, 0), 2)
        ax.imshow(vis); ax.axis('off'); ax.set_title(f'{title}: {len(merged)} hộp', fontsize=10)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.4))
    draw(P.DILATE_ITER_SINGLE, P.MERGE_GAP_SINGLE, '1 chữ số (gộp gap=10)', a1)
    draw(P.DILATE_ITER_MULTI, P.MERGE_GAP_MULTI, 'Nhiều chữ số (gộp gap=30)', a2)
    plt.tight_layout(); plt.savefig(os.path.join(OUT, 'hinh_3_8_single_vs_multi.png'), dpi=200); plt.close()
    print(f'Tách được {len(digits)} chữ số (chế độ nhiều chữ số). Lỗi: {err}')
    print(f'Đã lưu hình vào thư mục {OUT}/')


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == 'eval':
        run_eval()
    elif len(sys.argv) >= 3 and sys.argv[1] == 'preprocess':
        run_preprocess(sys.argv[2])
    else:
        print(__doc__)
