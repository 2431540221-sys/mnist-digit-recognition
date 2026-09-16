"""
Module tiền xử lý và phân đoạn ảnh chữ số viết tay, dùng OpenCV.

Pipeline xử lý ảnh áp dụng (đúng các bước cơ bản trong môn Xử lý ảnh & Thị giác máy tính):
1. Chuyển ảnh màu -> ảnh xám (grayscale)
2. Làm mịn nhiễu bằng Gaussian Blur
3. Phân ngưỡng nhị phân (Otsu thresholding) -> ảnh nhị phân đen/trắng
4. Phép toán hình thái học Dilation -> làm dày nét vẽ mảnh
5. Contour Detection -> tìm và tách từng vùng chữ số (segmentation)
6. Chuẩn hóa từng chữ số về đúng định dạng ảnh MNIST (28x28, canh giữa)
"""

import cv2
import numpy as np
from PIL import Image


def _pil_to_cv2_gray(img: Image.Image) -> np.ndarray:
    """Chuyển ảnh PIL sang mảng OpenCV grayscale (uint8)."""
    img_rgb = img.convert('RGB')
    cv_img = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    return gray


def _binarize(img: Image.Image) -> np.ndarray:
    """
    Bước 1-4 của pipeline: grayscale -> blur -> threshold (Otsu) -> dilation.
    Trả về ảnh nhị phân: nền đen (0), chữ số trắng (255) - đúng chuẩn MNIST.
    """
    gray = _pil_to_cv2_gray(img)

    # Tự phát hiện nền sáng/tối dựa vào 4 góc ảnh, đảo màu nếu nền sáng
    corners_mean = np.mean([
        gray[0, 0], gray[0, -1], gray[-1, 0], gray[-1, -1]
    ])
    if corners_mean > 127:
        gray = 255 - gray

    # Gaussian Blur: làm mịn nhiễu trước khi threshold, giảm răng cưa của nét vẽ
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Otsu Thresholding: tự động tìm ngưỡng nhị phân tối ưu thay vì chọn tay 1 số cố định
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Dilation: làm dày nét vẽ mảnh (giải quyết vấn đề nét vẽ chuột quá mảnh
    # khiến model đoán sai độ tin cậy thấp), đồng thời giúp nối lại các
    # điểm nét gần đứt (ví dụ chỗ nối giữa nét serif và thân số 1)
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv2.dilate(binary, kernel, iterations=3)

    return dilated


def _center_digit(digit_crop: np.ndarray) -> np.ndarray:
    """Resize giữ tỉ lệ khung hình và đặt 1 chữ số đã crop vào giữa khung 28x28."""
    h, w = digit_crop.shape
    if h > w:
        new_h, new_w = 20, max(1, int(w * 20 / h))
    else:
        new_w, new_h = 20, max(1, int(h * 20 / w))

    resized = cv2.resize(digit_crop, (new_w, new_h), interpolation=cv2.INTER_AREA)

    canvas = np.zeros((28, 28), dtype=np.uint8)
    x_off = (28 - new_w) // 2
    y_off = (28 - new_h) // 2
    canvas[y_off:y_off + new_h, x_off:x_off + new_w] = resized

    normalized = canvas.astype('float32') / 255
    return normalized.reshape(28, 28, 1)


def preprocess_image(img: Image.Image):
    """Xử lý ảnh chỉ có 1 chữ số (dùng cho /predict). Trả về (1, 28, 28, 1) hoặc None."""
    binary = _binarize(img)
    coords = cv2.findNonZero(binary)
    if coords is None:
        return None

    x, y, w, h = cv2.boundingRect(coords)
    digit_crop = binary[y:y + h, x:x + w]
    result = _center_digit(digit_crop)
    return result.reshape(1, 28, 28, 1)


def _merge_close_boxes(boxes, merge_gap=10):
    """
    Gộp các bounding box nằm rất gần nhau theo chiều ngang thành 1 box duy nhất.
    Cần thiết vì 1 chữ số có thể bị Contour Detection tách thành nhiều mảnh
    rời nhau do răng cưa/khử nhiễu (ví dụ: nét serif của số 1, vòng cong
    của số 2). Dilation ở bước _binarize đã nối được phần lớn các nét đứt,
    nên merge_gap chỉ cần nhỏ (10px) để dọn nốt phần còn sót, tránh gộp
    nhầm 2 chữ số khác nhau đứng gần nhau.
    """
    if not boxes:
        return []

    boxes = sorted(boxes, key=lambda b: b[0])  # sắp theo x
    merged = [list(boxes[0])]  # [x, y, w, h] có thể sửa được

    for x, y, w, h in boxes[1:]:
        last = merged[-1]
        last_right = last[0] + last[2]
        gap = x - last_right

        if gap < merge_gap:
            # Gộp: mở rộng box cuối cùng để bao trùm cả box hiện tại
            new_x0 = min(last[0], x)
            new_y0 = min(last[1], y)
            new_x1 = max(last[0] + last[2], x + w)
            new_y1 = max(last[1] + last[3], y + h)
            last[0], last[1] = new_x0, new_y0
            last[2], last[3] = new_x1 - new_x0, new_y1 - new_y0
        else:
            merged.append([x, y, w, h])

    return merged


def segment_digits(img: Image.Image, min_area=15, merge_gap=10):
    """
    Bước 5 của pipeline: dùng Contour Detection (cv2.findContours) để tìm
    các vùng có nét vẽ, gộp các mảnh vỡ rất gần nhau thuộc cùng 1 chữ số
    (_merge_close_boxes), rồi tách thành từng chữ số riêng biệt theo
    thứ tự trái -> phải. Trả về list các mảng (28, 28, 1).
    """
    binary = _binarize(img)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    raw_boxes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        raw_boxes.append(cv2.boundingRect(cnt))

    boxes = _merge_close_boxes(raw_boxes, merge_gap=merge_gap)
    boxes.sort(key=lambda b: b[0])

    digits = []
    for x, y, w, h in boxes:
        digit_crop = binary[y:y + h, x:x + w]
        digits.append(_center_digit(digit_crop))

    return digits


# Alias tương thích
segment_single_digit = preprocess_image
segment_multi_digits = segment_digits
