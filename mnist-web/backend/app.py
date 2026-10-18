from flask import Flask, request, jsonify
from flask_cors import CORS
from keras.models import load_model
import numpy as np
from PIL import Image
import base64
import io
import sys

# Fix UnicodeEncodeError khi in tiếng Việt trên Windows console (cp1252/cp1258)
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from preprocessing import preprocess_image, segment_digits, segment_multi_digits

app = Flask(__name__)
CORS(app)  # Cho phép Vue (chạy ở port khác) gọi API này

# Load model 1 lần duy nhất khi server khởi động
model = load_model('models/mnist_cnn_model.h5')
print("Model đã load thành công")


# Ngưỡng confidence để đánh dấu "không chắc chắn" — khi top-1 < ngưỡng này,
# frontend sẽ hiển thị top-3 để user chọn (giải quyết nhầm 2↔3, 4↔7, ...)
LOW_CONFIDENCE_THRESHOLD = 0.70


def _top_k_predictions(prob_vector: np.ndarray, k: int = 3) -> list:
    """
    Lấy top-k chữ số có xác suất cao nhất.
    Trả về list các dict { 'digit': int, 'probability': float } sắp giảm dần.
    """
    indices = np.argsort(prob_vector)[::-1][:k]
    return [
        {'digit': int(i), 'probability': float(prob_vector[i])}
        for i in indices
    ]


def _build_result(pred_vector: np.ndarray) -> dict:
    """
    Tạo dict kết quả dự đoán chuẩn từ vector xác suất (softmax output).
    Bao gồm digit, confidence, full probabilities, top-3, low_confidence flag.
    """
    digit = int(np.argmax(pred_vector))
    confidence = float(np.max(pred_vector))
    probabilities = {str(i): float(p) for i, p in enumerate(pred_vector)}
    top_3 = _top_k_predictions(pred_vector, k=3)
    return {
        'digit': digit,
        'confidence': confidence,
        'probabilities': probabilities,
        'top_3': top_3,
        'low_confidence': confidence < LOW_CONFIDENCE_THRESHOLD,
    }


def decode_base64_image(image_data):
    header, encoded = image_data.split(',', 1)
    img_bytes = base64.b64decode(encoded)
    return Image.open(io.BytesIO(img_bytes))


@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint chính xử lý yêu cầu từ Web Frontend (hỗ trợ cả mode='single' và mode='multi')."""
    data = request.get_json()
    image_data = data.get('image')
    mode = data.get('mode', 'single')

    if not image_data:
        return jsonify({'error': 'Thiếu dữ liệu ảnh'}), 400

    img = decode_base64_image(image_data)

    if mode == 'single':
        processed = preprocess_image(img)
        if processed is None:
            return jsonify({'error': 'Không tìm thấy nét vẽ nào'}), 400

        prediction = model.predict(processed)
        result = _build_result(prediction[0])
        return jsonify({
            'digit': result['digit'],
            'confidence': result['confidence'],
            'probabilities': result['probabilities'],
            'top_3': result['top_3'],
            'low_confidence': result['low_confidence'],
            'results': [result],
        })
    else:
        # Multi-digit: dùng pipeline tối ưu (dilation nhẹ + merge_gap lớn
        # + projection profile tách tiếp box dính nhau)
        digit_arrays = segment_multi_digits(img)
        if len(digit_arrays) == 0:
            return jsonify({'error': 'Không tìm thấy chữ số nào'}), 400

        batch = np.stack(digit_arrays, axis=0)  # (n, 28, 28, 1)
        predictions = model.predict(batch)

        results = [_build_result(pred) for pred in predictions]
        number_string = ''.join(str(r['digit']) for r in results)
        return jsonify({
            'number': number_string,
            'digits': results,
            'results': results,
        })


@app.route('/predict-multi', methods=['POST'])
def predict_multi():
    """Dự đoán nhiều chữ số viết cạnh nhau, ghép thành 1 số hoàn chỉnh."""
    data = request.get_json()
    image_data = data.get('image')
    if not image_data:
        return jsonify({'error': 'Thiếu dữ liệu ảnh'}), 400

    img = decode_base64_image(image_data)
    digit_arrays = segment_multi_digits(img)

    if len(digit_arrays) == 0:
        return jsonify({'error': 'Không tìm thấy chữ số nào'}), 400

    batch = np.stack(digit_arrays, axis=0)  # (n, 28, 28, 1)
    predictions = model.predict(batch)

    results = [_build_result(pred) for pred in predictions]
    number_string = ''.join(str(r['digit']) for r in results)
    return jsonify({'number': number_string, 'digits': results})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/debug-segments', methods=['POST'])
def debug_segments():
    """Trả về số lượng chữ số tách được để debug."""
    data = request.get_json()
    image_data = data.get('image')
    if not image_data:
        return jsonify({'error': 'Thiếu dữ liệu ảnh'}), 400

    img = decode_base64_image(image_data)
    digit_arrays_single = segment_digits(img, merge_gap=10, dilate_iter=3)
    digit_arrays_multi  = segment_multi_digits(img)

    return jsonify({
        'so_luong_tach_duoc_single_mode': len(digit_arrays_single),
        'so_luong_tach_duoc_multi_mode':  len(digit_arrays_multi),
        'ghi_chu': (
            'Nếu số tách được khác với số chữ số bạn thực sự vẽ, '
            'hãy vẽ tách rời hơn (cách nhau >= 30px trên canvas 280px) '
            'hoặc chỉnh DILATE_ITER_MULTI / MERGE_GAP_MULTI trong preprocessing.py'
        )
    })


if __name__ == '__main__':
    # Trong production, chạy bằng gunicorn: `gunicorn app:app`
    # Trong dev, chạy bằng `python app.py`
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    app.run(debug=debug, host='0.0.0.0', port=port)
