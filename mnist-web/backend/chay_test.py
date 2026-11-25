import os, glob, time, base64, statistics, requests

URL = "http://127.0.0.1:5000/predict"   # đổi cổng nếu backend của bạn khác
FOLDER = "test_multi"
LAN_DO = 3                               # đo mỗi ảnh 3 lần để lấy thời gian trung bình

def goi(path, mode="multi"):
    raw = base64.b64encode(open(path, "rb").read()).decode()
    # thử có tiền tố data URL trước, nếu backend báo lỗi thì thử không có
    for img in ("data:image/png;base64," + raw, raw):
        t = time.perf_counter()
        r = requests.post(URL, json={"image": img, "mode": mode})
        ms = (time.perf_counter() - t) * 1000
        if r.status_code == 200:
            return r.json(), ms
    return None, 0

nhom = {}       # "2" / "3" / "4" -> [số ảnh, tách đúng, đọc đúng]
sai = []
thoi_gian = []

for p in sorted(glob.glob(os.path.join(FOLDER, "*.png"))):
    ten = os.path.basename(p)
    nhan = ten.split("_")[0]
    k = str(min(len(nhan), 4))
    s = nhom.setdefault(k, [0, 0, 0]); s[0] += 1

    kq, ms = goi(p)
    if kq is None:
        sai.append((ten, "lỗi gọi API")); continue
    thoi_gian.append(ms)
    for _ in range(LAN_DO - 1):
        thoi_gian.append(goi(p)[1])

    doc = str(kq.get("number", ""))
    tach_dung = len(kq.get("digits", [])) == len(nhan)
    doc_dung = doc == nhan
    s[1] += tach_dung; s[2] += doc_dung
    if not doc_dung:
        sai.append((ten, f"đọc ra {doc!r}, tách đúng số chữ số: {tach_dung}"))

print("\nSố chữ số | Số ảnh | Tách đúng | Đọc đúng")
tong = [0, 0, 0]
for k in sorted(nhom):
    n, a, b = nhom[k]
    print(f"{k:>9} | {n:>6} | {a:>9} | {b:>8}")
    tong = [tong[0]+n, tong[1]+a, tong[2]+b]
print(f"{'Tổng':>9} | {tong[0]:>6} | {tong[1]:>9} | {tong[2]:>8}")

print("\nẢnh đọc sai:")
for ten, lydo in sai: print(" -", ten, "->", lydo)

print(f"\nThời gian trung bình chế độ nhiều chữ số: "
      f"{statistics.mean(thoi_gian):.0f} ms ({len(thoi_gian)} lần đo)")