"""Chạy thử hàng loạt ảnh ngoài ở chế độ 1 chữ số, thống kê cho Bảng 3.12.
Cách dùng:
  1. Bật backend:  python app.py   (cổng 5000)
  2. Đặt ảnh vào một thư mục, tên file bắt đầu bằng nhãn thật rồi dấu gạch dưới, ví dụ:
        0_01.png  0_02.jpg  3_01.png  7_05.jpeg ...
  3. Chạy:  python kiem_thu_anh_ngoai.py thu_muc_anh
Cần thư viện requests:  pip install requests
Kết quả in ra màn hình và lưu vào ket_qua_anh_ngoai.csv.
"""
import base64, csv, mimetypes, os, sys
import requests

URL = os.environ.get("API_URL", "http://localhost:5000/predict")
folder = sys.argv[1]
stats = {d: {"n": 0, "ok": 0, "reject": 0} for d in range(10)}
rows = []

for name in sorted(os.listdir(folder)):
    if not name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".webp")):
        continue
    if not name[0].isdigit():
        print("Bỏ qua (tên không bắt đầu bằng nhãn 0-9):", name); continue
    true = int(name[0])
    mime = mimetypes.guess_type(name)[0] or "image/png"
    with open(os.path.join(folder, name), "rb") as f:
        data_url = f"data:{mime};base64," + base64.b64encode(f.read()).decode()
    stats[true]["n"] += 1
    pred, conf, status = None, None, ""
    try:
        r = requests.post(URL, json={"image": data_url, "mode": "single"}, timeout=60)
        if r.status_code == 200:
            j = r.json()
            first = (j.get("results") or [{}])[0]
            pred = first.get("digit", j.get("digit"))
            conf = first.get("confidence", j.get("confidence"))
            status = "đúng" if pred == true else "sai"
        else:
            status = "bị từ chối"
            stats[true]["reject"] += 1
    except Exception as e:
        status = "lỗi kết nối: %s" % e
    if status == "đúng":
        stats[true]["ok"] += 1
    rows.append([name, true, pred, None if conf is None else round(conf, 3), status])
    print(f"{name:25s} thật={true} đoán={pred} tin cậy={conf} -> {status}")

print("\nChữ số | Số ảnh thử | Nhận diện đúng | Tỉ lệ đúng | (bị từ chối)")
tn = tok = 0
for d in range(10):
    s = stats[d]; tn += s["n"]; tok += s["ok"]
    rate = "%.1f%%" % (100 * s["ok"] / s["n"]) if s["n"] else "-"
    print(f"{d:6d} | {s['n']:10d} | {s['ok']:14d} | {rate:>10s} | {s['reject']}")
print("Tổng   | %10d | %14d | %9.1f%%" % (tn, tok, 100 * tok / tn if tn else 0))

with open("ket_qua_anh_ngoai.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["file", "nhan_that", "du_doan", "tin_cay", "ket_qua"]); w.writerows(rows)
print("Đã lưu ket_qua_anh_ngoai.csv")
