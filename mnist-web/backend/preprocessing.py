"""
Module tiền xử lý và phân đoạn ảnh chữ số viết tay, dùng OpenCV.

Pipeline xử lý ảnh áp dụng (đúng các bước cơ bản trong môn Xử lý ảnh & Thị giác máy tính):
1. Chuyển ảnh màu -> ảnh xám (grayscale)
2. Làm mịn nhiễu bằng Gaussian Blur
3. Phân ngưỡng nhị phân (Otsu thresholding) -> ảnh nhị phân đen/trắng
4. Phép toán hình thái học Dilation (CHỈ dùng cho 1 chữ số; multi-digit
   dùng dilation nhẹ hơn để tránh 2 số dính nhau)
5. Contour Detection + Projection Profile -> tìm và tách từng vùng chữ số
6. Chuẩn hóa từng chữ số về đúng định dạng ảnh MNIST (28x28, canh giữa)
"""

import cv2
import numpy as np
from PIL import Image


# =============================================================================
# CÁC HẰNG SỐ CẤU HÌNH CHO 2 CHẾ ĐỘ
# =============================================================================
# Single-digit: nét vẽ mảnh (touchpad, chuột nhỏ) nên cần dilation mạnh + merge
#               các mảnh vỡ của 1 số (vd: số 1 có serif tách rời, số 2 vòng hở).
# Multi-digit:  ưu tiên tách rời 2 số đứng gần, dilation nhẹ + merge_gap lớn hơn.

DILATE_ITER_SINGLE = 3    # iteration dilation cho mode 1 số (nét dày để bắt mảnh vỡ)
DILATE_ITER_MULTI  = 1    # iteration dilation cho mode nhiều số (giữ tách rời)
DILATE_KERNEL      = (3, 3)

MERGE_GAP_SINGLE   = 10   # px - gộp box của 1 số nếu cách < 10px
MERGE_GAP_MULTI    = 30   # px - hạn chế gộp nhầm 2 số khác nhau

MIN_AREA           = 15   # loại bỏ contour quá nhỏ (nhiễu, dấu chấm)


# =============================================================================
# CÁC HÀM TIỆN ÍCH
# =============================================================================
def _pil_to_cv2_gray(img: Image.Image) -> np.ndarray:
    """Chuyển ảnh PIL sang mảng OpenCV grayscale (uint8)."""
    img_rgb = img.convert('RGB')
    cv_img = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    return gray


def _binarize(img: Image.Image, dilate_iter: int = DILATE_ITER_SINGLE) -> np.ndarray:
    """
    Bước 1-4 của pipeline: grayscale -> blur -> threshold (Otsu) -> dilation.
    Trả về ảnh nhị phân: nền đen (0), chữ số trắng (255) - đúng chuẩn MNIST.

    Tham số `dilate_iter` được tách riêng cho từng chế độ single/multi.
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

    # Otsu Thresholding: tự động tìm ngưỡng nhị phân tối ưu
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    if dilate_iter > 0:
        # Dilation: nối các điểm nét gần đứt; iteration cao hơn = nét dày hơn.
        # Multi-digit dùng iter nhỏ (1) để tránh 2 số dính nhau.
        kernel = np.ones(DILATE_KERNEL, np.uint8)
        binary = cv2.dilate(binary, kernel, iterations=dilate_iter)

    return binary


def _center_digit(digit_crop: np.ndarray) -> np.ndarray:
    """Resize giữ tỉ lệ khung hình và đặt 1 chữ số đã crop vào giữa khung 28x28."""
    h, w = digit_crop.shape
    if h == 0 or w == 0:
        return np.zeros((28, 28, 1), dtype='float32')

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


# =============================================================================
# BƯỚC 5A: GỘP CÁC MẢNH VỠ CÙNG MỘT CHỮ SỐ
# =============================================================================
# Ngưỡng cho bước gộp dọc (với ảnh user vẽ số "1" có gạch ngang dưới,
# contour tách thành 2 box dọc — thân "1" và gạch ngang. Nếu 2 box
# nằm cùng cột x, cách nhau < VERT_GAP_PX và chiều rộng chênh < 50%,
# coi như cùng 1 số).
VERT_MERGE_GAP       = 25    # px khoảng cách dọc tối đa để gộp
VERT_MERGE_WIDTH_RATIO = 0.5  # tỉ lệ chênh lệch chiều rộng cho phép


def _merge_close_boxes(boxes, merge_gap: int = MERGE_GAP_SINGLE):
    """
    Gộp các bounding box nằm rất gần nhau thành 1 box duy nhất theo 2 chiều.

    (1) Gộp NGANG: khi 2 box cùng hàng (khoảng cách ngang < merge_gap VÀ
        chồng lấn dọc > 30%). Cần thiết vì 1 chữ số có thể bị Contour
        Detection tách thành nhiều mảnh ngang rời nhau do răng cưa.

    (2) Gộp DỌC:  khi 2 box cùng cột (khoảng cách dọc < VERT_MERGE_GAP
        VÀ chiều rộng chênh lệch < 50%). Cần thiết vì:
        - Số "1" có gạch ngang dưới (serif) bị tách rời khỏi thân
        - Số "7" có gạch ngang giữa có thể bị tách rời
        Tránh gộp nhầm: chỉ chạy khi chiều rộng 2 box tương đương
        (gạch ngang thường dài bằng hoặc ngắn hơn thân số một chút).
    """
    if not boxes:
        return []

    # Sắp theo x tăng dần để merge ngang trước
    boxes = sorted(boxes, key=lambda b: b[0])
    merged_h = [list(boxes[0])]  # [x, y, w, h] có thể sửa được

    # --- PASS 1: GỘP NGANG ---
    for x, y, w, h in boxes[1:]:
        last = merged_h[-1]
        last_right = last[0] + last[2]
        gap = x - last_right
        y_overlap = min(last[1] + last[3], y + h) - max(last[1], y)
        min_h = min(last[3], h)
        overlap_y_ratio = y_overlap / min_h if min_h > 0 else 0

        if gap < merge_gap and overlap_y_ratio > 0.3:
            # Gộp ngang: mở rộng box cuối cùng để bao trùm cả box hiện tại
            new_x0 = min(last[0], x)
            new_y0 = min(last[1], y)
            new_x1 = max(last[0] + last[2], x + w)
            new_y1 = max(last[1] + last[3], y + h)
            last[0], last[1] = new_x0, new_y0
            last[2], last[3] = new_x1 - new_x0, new_y1 - new_y0
        else:
            merged_h.append([x, y, w, h])

    # --- PASS 2: GỘP DỌC ---
    # Sắp theo y để duyệt từ trên xuống dưới
    merged_h.sort(key=lambda b: b[1])
    merged = [list(merged_h[0])]
    for x, y, w, h in merged_h[1:]:
        last = merged[-1]
        last_bottom = last[1] + last[3]
        v_gap = y - last_bottom

        # Điều kiện gộp dọc:
        # - khoảng cách dọc < VERT_MERGE_GAP
        # - x-overlap lớn (cùng cột) — box dưới nằm trong box trên theo chiều ngang
        # - chiều rộng tương đương (chênh < 50%)
        x_overlap = min(last[0] + last[2], x + w) - max(last[0], x)
        x_overlap_ratio = x_overlap / min(last[2], w) if min(last[2], w) > 0 else 0
        width_ratio = min(last[2], w) / max(last[2], w) if max(last[2], w) > 0 else 0

        if v_gap >= 0 and v_gap < VERT_MERGE_GAP and x_overlap_ratio > 0.5 and width_ratio > VERT_MERGE_WIDTH_RATIO:
            # Gộp dọc: mở rộng box cuối cùng để bao trùm cả box dưới
            new_x0 = min(last[0], x)
            new_y0 = last[1]
            new_x1 = max(last[0] + last[2], x + w)
            new_y1 = y + h
            last[0], last[1] = new_x0, new_y0
            last[2], last[3] = new_x1 - new_x0, new_y1 - new_y0
        else:
            merged.append([x, y, w, h])

    # Sắp lại theo x để đảm bảo thứ tự trái → phải
    merged.sort(key=lambda b: b[0])
    return merged


# =============================================================================
# BƯỚC 5B: TÁCH KHOẢNG TRỐNG GIỮA CÁC SỐ BẰNG PROJECTION PROFILE
# =============================================================================
def _split_box_by_projection(binary: np.ndarray, x: int, y: int, w: int, h: int,
                              min_gap_px: int = 6) -> list:
    """
    Nếu 1 bounding box quá rộng (có thể chứa 2+ số bị dính nhau), dùng
    Vertical Projection Profile (đếm pixel trắng theo từng cột) để tìm
    các "khoảng trống" dọc và tách box thành nhiều box con.

    Tách tại các cột có số pixel trắng == 0 và khoảng trống kéo dài >= min_gap_px.
    Trả về danh sách [x, y, w, h] mới (đã loại bỏ box quá mỏng).
    """
    if w <= 0 or h <= 0:
        return [[x, y, w, h]]

    region = binary[y:y + h, x:x + w]            # vùng con
    col_sum = (region > 0).sum(axis=0)            # đếm pixel trắng theo từng cột

    # Tìm các vùng "trống" (col_sum == 0) liên tiếp
    is_gap = (col_sum == 0).astype(np.uint8)
    # Đánh dấu các gap có độ dài >= min_gap_px
    gap_runs = []
    i = 0
    while i < len(is_gap):
        if is_gap[i] == 1:
            j = i
            while j < len(is_gap) and is_gap[j] == 1:
                j += 1
            run_len = j - i
            if run_len >= min_gap_px:
                gap_runs.append((i, j))   # [start, end) trong hệ toạ độ region
            i = j
        else:
            i += 1

    if not gap_runs:
        return [[x, y, w, h]]

    # Cắt region thành các sub-box theo các gap
    sub_boxes = []
    cursor = 0
    for g_start, g_end in gap_runs:
        seg_w = g_start - cursor
        if seg_w >= 5:    # bỏ qua mảnh quá hẹp
            sub_boxes.append([x + cursor, y, seg_w, h])
        cursor = g_end
    # Đoạn cuối
    if len(col_sum) - cursor >= 5:
        sub_boxes.append([x + cursor, y, len(col_sum) - cursor, h])

    return sub_boxes if sub_boxes else [[x, y, w, h]]


# =============================================================================
# CÁC HÀM PUBLIC (API của module)
# =============================================================================
def preprocess_image(img: Image.Image):
    """
    Xử lý ảnh chỉ có 1 chữ số (dùng cho /predict mode=single).
    Trả về numpy array shape (1, 28, 28, 1) hoặc None nếu ảnh rỗng.
    """
    binary = _binarize(img, dilate_iter=DILATE_ITER_SINGLE)
    coords = cv2.findNonZero(binary)
    if coords is None:
        return None

    x, y, w, h = cv2.boundingRect(coords)
    digit_crop = binary[y:y + h, x:x + w]
    result = _center_digit(digit_crop)
    return result.reshape(1, 28, 28, 1)


def segment_digits(img: Image.Image, min_area: int = MIN_AREA,
                   merge_gap: int = MERGE_GAP_SINGLE,
                   dilate_iter: int = DILATE_ITER_SINGLE) -> list:
    """
    Bước 5 của pipeline: dùng Contour Detection (cv2.findContours) để tìm
    các vùng có nét vẽ, gộp các mảnh vỡ rất gần nhau thuộc cùng 1 chữ số
    (_merge_close_boxes), rồi dùng projection profile để tách tiếp nếu
    box vẫn quá rộng (gộp nhầm 2 số), cuối cùng canh giữa và resize về 28x28.
    Trả về list các mảng (28, 28, 1).
    """
    binary = _binarize(img, dilate_iter=dilate_iter)

    # 1) Tìm contour ngoài cùng (RETR_EXTERNAL) - đủ cho chữ viết tay liền nét
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    raw_boxes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        raw_boxes.append(cv2.boundingRect(cnt))

    # 2) Gộp các mảnh vỡ của cùng 1 số
    boxes = _merge_close_boxes(raw_boxes, merge_gap=merge_gap)

    # 3) Dùng projection profile tách tiếp các box còn quá rộng
    final_boxes = []
    for (x, y, w, h) in boxes:
        sub = _split_box_by_projection(binary, x, y, w, h, min_gap_px=6)
        final_boxes.extend(sub)

    # 4) Loại box quá nhỏ, sort theo x tăng dần (trái -> phải)
    final_boxes = [b for b in final_boxes if b[2] >= 5 and b[3] >= 5]
    final_boxes.sort(key=lambda b: b[0])

    digits = []
    for x, y, w, h in final_boxes:
        digit_crop = binary[y:y + h, x:x + w]
        digits.append(_center_digit(digit_crop))

    return digits


# Hàm chuyên biệt cho multi-digit - dùng dilation nhẹ + merge_gap lớn
def segment_multi_digits(img: Image.Image) -> list:
    """Pipeline tối ưu cho ảnh có nhiều chữ số viết cạnh nhau."""
    return segment_digits(
        img,
        min_area=MIN_AREA,
        merge_gap=MERGE_GAP_MULTI,
        dilate_iter=DILATE_ITER_MULTI,
    )


# Alias tương thích với code cũ
segment_single_digit = preprocess_image
