"""Đo thời gian phản hồi của API /predict.

Cách dùng (backend Flask phải đang chạy):
    python bench_latency.py anh_mau.png --mode single
    python bench_latency.py anh_123.png --mode multi -n 90

Kết quả: trung bình, trung vị, nhỏ nhất, lớn nhất, p95 (mili giây).
"""
import argparse
import base64
import mimetypes
import statistics
import sys
import time

import requests


def to_data_url(path):
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image", help="đường dẫn ảnh dùng để đo")
    ap.add_argument("--mode", choices=["single", "multi"], default="single")
    ap.add_argument("--url", default="http://localhost:5000/predict")
    ap.add_argument("-n", type=int, default=90, help="số lần đo (mặc định 90)")
    ap.add_argument("--warmup", type=int, default=5, help="số lần chạy khởi động, không tính")
    args = ap.parse_args()

    payload = {"image": to_data_url(args.image), "mode": args.mode}
    session = requests.Session()

    for _ in range(args.warmup):
        r = session.post(args.url, json=payload, timeout=30)
        if r.status_code != 200:
            sys.exit(f"Lỗi {r.status_code}: {r.text[:200]}")

    times = []
    for _ in range(args.n):
        t0 = time.perf_counter()
        r = session.post(args.url, json=payload, timeout=30)
        times.append((time.perf_counter() - t0) * 1000)
        if r.status_code != 200:
            sys.exit(f"Lỗi {r.status_code}: {r.text[:200]}")

    times.sort()
    p95 = times[min(len(times) - 1, int(round(0.95 * len(times))) - 1)]
    print(f"Chế độ: {args.mode} | số lần đo: {len(times)} (bỏ {args.warmup} lần khởi động)")
    print(f"Trung bình : {statistics.mean(times):.1f} ms")
    print(f"Trung vị   : {statistics.median(times):.1f} ms")
    print(f"Nhỏ nhất   : {times[0]:.1f} ms")
    print(f"Lớn nhất   : {times[-1]:.1f} ms")
    print(f"p95        : {p95:.1f} ms")


if __name__ == "__main__":
    main()
