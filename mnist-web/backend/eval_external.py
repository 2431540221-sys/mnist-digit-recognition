"""Chạy lại bộ ảnh ngoài (chế độ 1 chữ số) qua API /predict.

Nhãn thật được lấy theo một trong hai cách:
  - ảnh nằm trong thư mục tên là chữ số:  anh_ngoai/3/abc.png
  - hoặc tên file bắt đầu bằng chữ số:    anh_ngoai/3_01.png

Cách dùng (backend Flask phải đang chạy):
    python eval_external.py anh_ngoai

In ra: bảng đúng/sai theo từng chữ số (khớp Bảng 3.11) và danh sách ảnh sai
(tên file, nhãn thật, nhãn đoán, độ tin cậy, có bị cảnh báo độ tin cậy thấp hay
bị backend báo lỗi). Đồng thời lưu ket_qua_anh_ngoai.csv.
"""
import argparse
import base64
import csv
import mimetypes
import os
import sys

import requests

EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}


def to_data_url(path):
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def true_label(path):
    folder = os.path.basename(os.path.dirname(path))
    if len(folder) == 1 and folder.isdigit():
        return int(folder)
    stem = os.path.basename(path)
    if stem[0].isdigit():
        return int(stem[0])
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--url", default="http://localhost:5000/predict")
    ap.add_argument("--mode", default="single", choices=["single", "multi"])
    ap.add_argument("--csv", default="ket_qua_anh_ngoai.csv")
    args = ap.parse_args()

    files = []
    for root, _, names in os.walk(args.folder):
        for n in sorted(names):
            if os.path.splitext(n)[1].lower() in EXTS:
                files.append(os.path.join(root, n))
    files.sort()
    if not files:
        sys.exit("Không tìm thấy ảnh trong thư mục.")

    session = requests.Session()
    rows = []
    for path in files:
        truth = true_label(path)
        if truth is None:
            print(f"Bỏ qua (không xác định được nhãn): {path}")
            continue
        r = session.post(args.url, json={"image": to_data_url(path), "mode": args.mode}, timeout=30)
        pred, conf, low, note = None, None, None, ""
        if r.status_code == 200:
            d = r.json()
            pred, conf, low = d.get("digit"), d.get("confidence"), d.get("low_confidence")
        else:
            try:
                note = r.json().get("error", "")
            except Exception:
                note = r.text[:80]
            note = f"HTTP {r.status_code}: {note}"
        rows.append({
            "file": os.path.relpath(path, args.folder), "that": truth, "doan": pred,
            "tin_cay": conf, "canh_bao_thap": low, "dung": pred == truth, "ghi_chu": note,
        })

    # Bảng theo chữ số
    print(f"\n{'Chữ số':<8}{'Số ảnh':<9}{'Đúng':<7}{'Tỉ lệ'}")
    total = correct = 0
    for d in range(10):
        sub = [x for x in rows if x["that"] == d]
        if not sub:
            continue
        ok = sum(x["dung"] for x in sub)
        total += len(sub)
        correct += ok
        print(f"{d:<8}{len(sub):<9}{ok:<7}{100 * ok / len(sub):.0f}%")
    print(f"{'Tổng':<8}{total:<9}{correct:<7}{100 * correct / max(total, 1):.0f}%")

    # Danh sách ảnh sai
    wrong = [x for x in rows if not x["dung"]]
    print(f"\nẢnh sai ({len(wrong)}):")
    for x in wrong:
        conf = "-" if x["tin_cay"] is None else f"{x['tin_cay'] * 100:.1f}%"
        print(f"  {x['file']}: thật={x['that']} | đoán={x['doan']} | tin cậy={conf} "
              f"| cảnh báo thấp={x['canh_bao_thap']} {x['ghi_chu']}")

    with open(args.csv, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nĐã lưu {args.csv}")


if __name__ == "__main__":
    main()
