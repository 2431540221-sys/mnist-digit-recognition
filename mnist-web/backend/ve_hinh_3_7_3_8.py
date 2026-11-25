"""Vẽ Hình 3.7 và 3.8 cho báo cáo (bản 2: mọi bước trung gian lấy từ hàm thật của preprocessing.py).
Chạy trong thư mục mnist-web/backend:
    python ve_hinh_3_7_3_8.py anh_123.png
Xuất ra hinh_3_7.png và hinh_3_8.png.
"""
import sys
import cv2, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
import preprocessing as P

img = Image.open(sys.argv[1]).convert("RGB")

# ---- các bước trung gian, gọi đúng hàm của backend ----
gray, _ = P._pil_to_cv2_gray(img)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
bw, _ = P._binarize(img, dilate_iter=0)                      # sau nhị phân hóa
dil, _ = P._binarize(img, dilate_iter=P.DILATE_ITER_MULTI)   # sau giãn nở (chế độ nhiều chữ số)
print("mean độ sáng = %.1f (dưới 35 -> Otsu, từ 35 trở lên -> ngưỡng thích nghi)" % gray.mean())

# ---- hộp bao: làm lại đúng các bước 2-5 của segment_digits ----
cnts, _ = cv2.findContours(dil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
raw = [cv2.boundingRect(c) for c in cnts if cv2.contourArea(c) >= P.MIN_AREA]
boxes = P._merge_close_boxes(raw, merge_gap=P.MERGE_GAP_MULTI) if raw else []
final = []
for (x, y, w, h) in boxes:
    final.extend(P._split_box_by_projection(dil, x, y, w, h, min_gap_px=6))
final = sorted([b for b in final if b[2] >= 5 and b[3] >= 5], key=lambda b: b[0])
boxed = cv2.cvtColor(dil, cv2.COLOR_GRAY2RGB)
for x, y, w, h in final:
    cv2.rectangle(boxed, (x, y), (x + w, y + h), (255, 0, 0), 2)

cells, err = P.segment_multi_digits(img)
cells = [np.squeeze(np.asarray(c)) for c in cells]
print("multi:", len(cells), "chữ số;", err)

# ---- Hình 3.7: một hàng ----
steps = [("Ảnh gốc", np.array(img)), ("Ảnh xám", gray), ("Sau lọc Gaussian", blur),
         ("Sau nhị phân hóa", bw), ("Sau giãn nở", dil), ("Hộp bao từng chữ số", boxed)]
n = len(steps) + len(cells)
fig, ax = plt.subplots(1, n, figsize=(2.2 * n, 2.8))
ax = np.atleast_1d(ax)
for a, (title, im) in zip(ax, steps):
    a.imshow(im, cmap=None if im.ndim == 3 else "gray"); a.set_title(title, fontsize=8)
for k, (a, c) in enumerate(zip(ax[len(steps):], cells), 1):
    a.imshow(c, cmap="gray"); a.set_title(f"Ô 28×28 #{k}", fontsize=8)
for a in ax: a.axis("off")
plt.tight_layout(); plt.savefig("hinh_3_7.png", dpi=200); plt.close()

# ---- Hình 3.8: chế độ 1 chữ số và nhiều chữ số trên cùng một ảnh ----
sarr, serr = P.preprocess_image(img)
print("single:", "OK" if sarr is not None else serr)
m = max(len(cells), 1)
fig = plt.figure(figsize=(2 * (m + 2), 4.6))
g = fig.add_gridspec(2, m + 1, width_ratios=[1.2] + [1] * m)
a = fig.add_subplot(g[0, 0]); a.axis("off")
if sarr is not None:
    a.imshow(np.squeeze(sarr), cmap="gray"); a.set_title("Chế độ 1 chữ số:\n1 ô 28×28 (cả ảnh)", fontsize=9)
else:
    a.text(0.5, 0.5, "Chế độ 1 chữ số:\nbị từ chối\n(" + serr[:45] + "…)", ha="center", va="center", fontsize=8, wrap=True)
a = fig.add_subplot(g[1, 0]); a.imshow(boxed); a.set_title("Chế độ nhiều chữ số:\ntách theo hộp bao", fontsize=9); a.axis("off")
for k, c in enumerate(cells):
    a = fig.add_subplot(g[1, k + 1]); a.imshow(c, cmap="gray"); a.set_title(f"#{k+1}", fontsize=9); a.axis("off")
plt.tight_layout(); plt.savefig("hinh_3_8.png", dpi=200)
print("Đã lưu hinh_3_7.png, hinh_3_8.png")