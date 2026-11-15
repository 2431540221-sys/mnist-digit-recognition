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

DILATE_ITER_SINGLE = 1    # Giảm xuống 1 để tránh bít kín các khe hở của số 3, 6, 8, 9, 0
DILATE_ITER_MULTI  = 1    # iteration dilation cho mode nhiều số (giữ tách rời)
DILATE_KERNEL      = (3, 3)

MERGE_GAP_SINGLE   = 10   # px - gộp box của 1 số nếu cách < 10px
MERGE_GAP_MULTI    = 30   # px - hạn chế gộp nhầm 2 số khác nhau

MIN_AREA           = 15   # loại bỏ contour quá nhỏ (nhiễu, dấu chấm)


# =============================================================================
# CÁC HÀM TIỆN ÍCH
# =============================================================================
def _pil_to_cv2_gray(img: Image.Image) -> tuple[np.ndarray, bool]:
    """
    Chuyển ảnh PIL sang mảng OpenCV grayscale (uint8).
    Đồng thời chuẩn hoá kích thước nếu ảnh quá lớn (> 800px) để đảm bảo
    tốc độ xử lý và tính nhất quán của các tham số morphological & thresholding.
    Trả về (gray, is_resized).
    """
    img_rgb = img.convert('RGB')
    cv_img = cv2.cvtColor(np.array(img_rgb), cv2.COLOR_RGB2BGR)

    h, w = cv_img.shape[:2]
    max_dim = max(h, w)
    is_resized = False
    if max_dim > 800:
        scale = 800.0 / max_dim
        new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
        cv_img = cv2.resize(cv_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        is_resized = True

    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    return gray, is_resized


def _binarize(img: Image.Image, dilate_iter: int = DILATE_ITER_SINGLE) -> tuple[np.ndarray, np.ndarray]:
    """
    Bước 1-4 của pipeline: grayscale -> phát hiện nguồn ảnh (canvas vs ảnh giấy/camera)
    -> Adaptive Threshold hoặc Otsu -> dilation & lọc nhiễu.
    Trả về:
      - binary: ảnh nhị phân nền đen (0), nét chữ trắng (255) - đúng chuẩn MNIST.
      - gray: ảnh xám đã chuẩn hoá kích thước.
    """
    gray, _ = _pil_to_cv2_gray(img)

    # 1. Kiểm tra nguồn ảnh:
    # Nếu là canvas vẽ tay: phần lớn pixel là màu đen (mean < 35)
    mean_val = np.mean(gray)
    median_val = np.median(gray)

    if mean_val < 35:
        # Canvas đen vẽ nét trắng: Gaussian Blur + Otsu Thresholding chuẩn
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    else:
        # Ảnh chụp từ Camera / Upload giấy có ánh sáng không đều & bóng mờ
        # Xác định nền giấy sáng hay tối dựa trên median
        is_light_bg = median_val > 90 or mean_val > 90
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Dùng Adaptive Thresholding để triệt tiêu toàn bộ bóng đổ & chênh sáng môi trường
        thresh_type = cv2.THRESH_BINARY_INV if is_light_bg else cv2.THRESH_BINARY
        binary = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, thresh_type, 31, 12
        )

        # Khử các chấm nhiễu muối tiêu nhỏ từ camera bằng Morphological Opening
        kernel_clean = np.ones((2, 2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_clean)

    if dilate_iter > 0:
        kernel = np.ones(DILATE_KERNEL, np.uint8)
        binary = cv2.dilate(binary, kernel, iterations=dilate_iter)

    return binary, gray


def _center_digit(digit_crop: np.ndarray) -> np.ndarray:
    """
    Resize giữ tỉ lệ khung hình vào hộp tối đa 20x20 và căn giữa theo
    Center of Mass (Trọng tâm pixel) đúng chuẩn tập dữ liệu MNIST.
    """
    h, w = digit_crop.shape
    if h == 0 or w == 0:
        return np.zeros((28, 28, 1), dtype='float32')

    if h > w:
        new_h, new_w = 20, max(1, int(w * 20 / h))
    else:
        new_w, new_h = 20, max(1, int(h * 20 / w))

    resized = cv2.resize(digit_crop, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # Đặt tạm vào giữa theo bounding box
    canvas = np.zeros((28, 28), dtype=np.float32)
    x_off = (28 - new_w) // 2
    y_off = (28 - new_h) // 2
    canvas[y_off:y_off + new_h, x_off:x_off + new_w] = resized.astype(np.float32)

    # Căn chỉnh lại theo Trọng tâm (Center of Mass) đúng chuẩn dataset MNIST (tâm tại 14.0, 14.0)
    M = cv2.moments(canvas)
    if M['m00'] > 0:
        cx = M['m10'] / M['m00']
        cy = M['m01'] / M['m00']
        shift_x = float(np.clip(14.0 - cx, -4.0, 4.0))
        shift_y = float(np.clip(14.0 - cy, -4.0, 4.0))
        M_shift = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
        canvas = cv2.warpAffine(canvas, M_shift, (28, 28), borderMode=cv2.BORDER_CONSTANT, borderValue=0)

    normalized = canvas / 255.0
    return normalized.reshape(28, 28, 1).astype('float32')


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
# KIỂM TRA TỔNG QUAN ẢNH (LOẠI BỎ ẢNH CHÂN DUNG, PHONG CẢNH, ĐỒ VẬT PHỨC TẠP)
# =============================================================================
def validate_image_is_digit_document(gray: np.ndarray, binary: np.ndarray, max_contours: int = 25) -> tuple:
    """
    Kiểm tra tổng quan toàn bộ bức ảnh:
    Nếu ảnh chứa quá nhiều contour lớn hoặc có mật độ cạnh Canny quá cao,
    đây là ảnh phong cảnh, chân dung, cảnh vật phức tạp, không phải tài liệu chữ số.
    Trả về (is_valid: bool, reason: str).
    """
    # 1. Số lượng external contours có diện tích đáng kể (> 20px)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    significant = [c for c in contours if cv2.contourArea(c) > 20]
    if len(significant) > max_contours:
        return False, f"Ảnh chứa quá nhiều chi tiết phức tạp ({len(significant)} vùng nét), nghi ngờ là ảnh chân dung hoặc phong cảnh, không phải chữ số viết tay."

    # 2. Mật độ cạnh Canny trên toàn bộ ảnh
    edges = cv2.Canny(gray, 50, 150)
    edge_ratio = float(np.sum(edges > 0)) / float(gray.shape[0] * gray.shape[1])
    if edge_ratio > 0.08:
        return False, "Ảnh có mật độ đường nét quá dày đặc, không phải chữ số viết tay trên nền phẳng."

    return True, "Hợp lệ"


def validate_digit_textline(boxes: list) -> tuple:
    """
    Ràng buộc cấu trúc dòng chữ số (Horizontal Text-line Constraint):
    Các chữ số viết tay luôn nằm trên cùng 1 hàng và có chiều cao tương đối đồng đều.
    Nếu các vùng phân đoạn rải rác từ đỉnh đầu xuống chân (như ảnh người), từ chối ngay.
    Trả về (is_valid: bool, reason: str).
    """
    if not boxes:
        return False, "Không tìm thấy nét chữ số nào."

    if len(boxes) > 10:
        return False, f"Phát hiện quá nhiều ký tự bất thường ({len(boxes)} ký tự). Hệ thống chỉ hỗ trợ tối đa 10 chữ số."

    if len(boxes) >= 2:
        heights = [b[3] for b in boxes]
        avg_h = float(np.mean(heights))
        if avg_h <= 0:
            return False, "Chiều cao ký tự không hợp lệ."

        min_top = min(b[1] for b in boxes)
        max_bottom = max(b[1] + b[3] for b in boxes)
        total_span_y = max_bottom - min_top

        # Nếu khoảng cách trải dọc gấp > 2.5 lần chiều cao trung bình của 1 số:
        if total_span_y > 2.5 * avg_h:
            return False, "Các ký tự phân tán rải rác theo chiều dọc, không tạo thành dòng chữ số hợp lệ (có thể do ảnh chụp chân dung hoặc đồ vật)."

        if len(boxes) >= 3:
            y_centers = [b[1] + b[3] / 2.0 for b in boxes]
            if float(np.std(y_centers)) > 1.2 * avg_h:
                return False, "Vị trí các ký tự không thẳng hàng (lệch dòng quá lớn)."

    return True, "Hợp lệ"


# =============================================================================
# KIỂM TRA HÌNH THÁI HỌC (LOẠI BỎ HÌNH VẼ BẬY, BÔI ĐEN, HOẶC KHÔNG PHẢI SỐ)
# =============================================================================
def validate_digit_morphology(digit_crop: np.ndarray) -> tuple:
    """
    Kiểm tra hình thái học để loại bỏ các hình vẽ không hợp lệ:
    1. Kích thước tối thiểu (tránh bụi/chấm nhỏ).
    2. Mật độ nét vẽ (tránh hình bôi đen kịt > 82% hoặc nét quá mờ nhạt < 4%).
    3. Tỉ lệ khung hình (tránh vệt gạch ngang/dọc bất thường).
    4. Số lượng lỗ hổng (Euler / Holes): Chữ số chỉ có tối đa 2 lỗ rỗng (số 8).
    Trả về (is_valid: bool, reason: str).
    """
    h, w = digit_crop.shape
    if h < 10 or w < 4:
        return False, "Nét vẽ quá nhỏ hoặc chỉ là chấm li ti."

    total_pixels = h * w
    white_pixels = int(np.sum(digit_crop == 255))
    density = white_pixels / float(total_pixels)

    # Mật độ nét vẽ: chỉ coi là khối bôi đen kịt nếu cả chiều rộng và chiều cao đủ lớn
    # (tránh loại nhầm số 1 viết thẳng có thanh hẹp w <= 16)
    if density > 0.88 and w > 16 and h > 16:
        return False, "Nét vẽ quá đặc hoặc bị bôi đen kịt, không giống chữ số."
    if density < 0.04:
        return False, "Nét vẽ quá mờ nhạt hoặc không đủ rõ nét."
    if white_pixels > 8500:
        return False, "Nét vẽ quá lớn hoặc bị bôi kín màn hình, không phải chữ số."

    aspect = w / float(h)
    if aspect > 3.8:
        return False, "Nét vẽ bị kéo quá dài theo chiều ngang."
    if aspect < 0.06:
        return False, "Nét vẽ quá mỏng dính bất thường."

    # Đếm số lỗ hổng bên trong bằng RETR_CCOMP (hierarchy cấp 2)
    contours, hierarchy = cv2.findContours(digit_crop, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is not None:
        holes = sum(1 for h_info in hierarchy[0] if h_info[3] != -1)
        if holes > 3:
            return False, f"Hình vẽ có quá nhiều lỗ rỗng ({holes} lỗ), không phải chữ số."

    return True, "Hợp lệ"


# =============================================================================
# CÁC HÀM PUBLIC (API của module)
# =============================================================================
def preprocess_image(img: Image.Image):
    """
    Xử lý ảnh chỉ có 1 chữ số (dùng cho /predict mode=single).
    Trả về tuple (numpy_array, None) nếu hợp lệ, hoặc (None, error_msg) nếu không hợp lệ.
    """
    binary, gray = _binarize(img, dilate_iter=DILATE_ITER_SINGLE)

    # 1. Kiểm tra ảnh tổng quan (đối với single-digit, số contour không thể vượt quá 12)
    is_doc, doc_msg = validate_image_is_digit_document(gray, binary, max_contours=12)
    if not is_doc:
        return None, doc_msg

    coords = cv2.findNonZero(binary)
    if coords is None:
        return None, "Không tìm thấy nét vẽ nào trong ảnh."

    x, y, w, h = cv2.boundingRect(coords)
    img_h, img_w = binary.shape[:2]

    # Kiểm tra kích thước: nếu bounding box chiếm gần trọn toàn bộ ảnh camera/upload (> 85%)
    # và bên trong có nhiều hơn 2 contour con -> ảnh chân dung/vật thể
    mean_val = np.mean(gray)
    if mean_val >= 35:  # Không phải canvas vẽ tay
        if (w > 0.85 * img_w) and (h > 0.85 * img_h):
            return None, "Vùng nét vẽ chiếm toàn bộ khung hình, không phải một chữ số đơn lẻ."

    digit_crop = binary[y:y + h, x:x + w]

    # Kiểm tra hình thái học
    is_valid, msg = validate_digit_morphology(digit_crop)
    if not is_valid:
        return None, msg

    result = _center_digit(digit_crop)
    return result.reshape(1, 28, 28, 1), None


def segment_digits(img: Image.Image, min_area: int = MIN_AREA,
                   merge_gap: int = MERGE_GAP_SINGLE,
                   dilate_iter: int = DILATE_ITER_SINGLE) -> tuple:
    """
    Bước 5 của pipeline: dùng Contour Detection (cv2.findContours) để tìm
    các vùng có nét vẽ, gộp các mảnh vỡ rất gần nhau thuộc cùng 1 chữ số
    (_merge_close_boxes), rồi dùng projection profile để tách tiếp nếu
    box vẫn quá rộng (gộp nhầm 2 số), cuối cùng canh giữa và resize về 28x28.
    Trả về (list_of_28x28_arrays, error_message_or_None).
    """
    binary, gray = _binarize(img, dilate_iter=dilate_iter)

    # 1) Kiểm tra tổng quan toàn ảnh
    is_doc, doc_msg = validate_image_is_digit_document(gray, binary, max_contours=25)
    if not is_doc:
        return [], doc_msg

    # 2) Tìm contour ngoài cùng (RETR_EXTERNAL) - đủ cho chữ viết tay liền nét
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    raw_boxes = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        raw_boxes.append(cv2.boundingRect(cnt))

    if not raw_boxes:
        return [], "Không tìm thấy nét chữ số nào trong ảnh."

    if len(raw_boxes) > 30:
        return [], "Ảnh chứa quá nhiều nét rời rạc, nghi ngờ là ảnh chân dung hoặc phong cảnh, không phải chữ số viết tay."

    # 3) Gộp các mảnh vỡ của cùng 1 số
    boxes = _merge_close_boxes(raw_boxes, merge_gap=merge_gap)

    # 4) Dùng projection profile tách tiếp các box còn quá rộng
    final_boxes = []
    for (x, y, w, h) in boxes:
        sub = _split_box_by_projection(binary, x, y, w, h, min_gap_px=6)
        final_boxes.extend(sub)

    # 5) Loại box quá nhỏ, sort theo x tăng dần (trái -> phải)
    final_boxes = [b for b in final_boxes if b[2] >= 5 and b[3] >= 5]
    final_boxes.sort(key=lambda b: b[0])

    if not final_boxes:
        return [], "Không tìm thấy ký tự hợp lệ nào sau khi phân đoạn."

    # 6) Kiểm tra ràng buộc cấu trúc dòng chữ số (Horizontal Text-line)
    is_line, line_msg = validate_digit_textline(final_boxes)
    if not is_line:
        return [], line_msg

    digits = []
    for x, y, w, h in final_boxes:
        digit_crop = binary[y:y + h, x:x + w]
        # Lọc qua kiểm tra hình thái học
        is_valid, _ = validate_digit_morphology(digit_crop)
        if is_valid:
            digits.append(_center_digit(digit_crop))

    if not digits:
        return [], "Các nét vẽ không thỏa mãn đặc trưng hình thái học của chữ số."

    return digits, None


# Hàm chuyên biệt cho multi-digit - dùng dilation nhẹ + merge_gap lớn
def segment_multi_digits(img: Image.Image) -> tuple:
    """Pipeline tối ưu cho ảnh có nhiều chữ số viết cạnh nhau. Trả về (digits, error_msg)."""
    return segment_digits(
        img,
        min_area=MIN_AREA,
        merge_gap=MERGE_GAP_MULTI,
        dilate_iter=DILATE_ITER_MULTI,
    )


# Alias tương thích với code cũ
segment_single_digit = preprocess_image
