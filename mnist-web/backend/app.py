from flask import Flask, request, jsonify
from flask_cors import CORS
import os
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
from model_info import build_model_info

app = Flask(__name__)

# CORS: trong production, chỉ cho phép frontend domain của mình
# Trong dev, cho phép tất cả để test trên local
_allowed_origins_env = os.environ.get('FRONTEND_URL', '').strip()
allowed_origins = [o for o in _allowed_origins_env.split(',') if o] if _allowed_origins_env else '*'
CORS(app, resources={r'/*': {'origins': allowed_origins}})

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


# Các bước xử lý của 1 request, dùng để báo lỗi xảy ra ở đâu:
#   input      -> dữ liệu gửi lên thiếu/hỏng, CHƯA tới tiền xử lý, CHƯA qua mô hình
#   preprocess -> lỗi lúc tách/chuẩn hóa chữ số,                   CHƯA qua mô hình
#   model      -> ảnh đã qua mô hình CNN nhưng kết quả không đủ tin cậy
ERROR_STAGES = ('input', 'preprocess', 'model')


def _error(message: str, stage: str, **extra):
    """Trả lỗi 400 kèm bước gây lỗi và cờ passed_model (đã đi qua mô hình CNN hay chưa)."""
    assert stage in ERROR_STAGES
    body = {'error': message, 'error_stage': stage, 'passed_model': stage == 'model'}
    body.update(extra)
    return jsonify(body), 400


def _read_image_from_request():
    """Đọc + giải mã ảnh từ request. Trả về (img, mode, error_response)."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, None, _error('Dữ liệu gửi lên không phải JSON hợp lệ.', 'input')
    image_data = data.get('image')
    if not image_data or not isinstance(image_data, str):
        return None, None, _error('Thiếu dữ liệu ảnh.', 'input')
    try:
        img = decode_base64_image(image_data)
        img.load()
    except Exception:
        return None, None, _error('Không đọc được ảnh gửi lên (sai định dạng base64/ảnh).', 'input')
    return img, data.get('mode', 'single'), None


@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint chính xử lý yêu cầu từ Web Frontend (hỗ trợ cả mode='single' và mode='multi')."""
    img, mode, err = _read_image_from_request()
    if err:
        return err

    if mode == 'single':
        processed, err_msg = preprocess_image(img)
        if processed is None:
            return _error(err_msg or 'Không tìm thấy nét vẽ nào', 'preprocess')

        prediction = model.predict(processed, verbose=0)
        result = _build_result(prediction[0])

        # Ngưỡng tin cậy tối thiểu: nếu < 60%, khả năng cao là hình vẽ bậy/không phải số
        if result['confidence'] < 0.60:
            return _error(
                f"Độ tin cậy quá thấp ({result['confidence']*100:.1f}%). Hình ảnh không giống chữ số từ 0 đến 9, vui lòng vẽ hoặc chụp rõ ràng hơn.",
                'model',
                confidence=result['confidence'],
            )

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
        # + projection profile tách tiếp box dính nhau + lọc ảnh chân dung/ngoại cảnh)
        digit_arrays, err_msg = segment_multi_digits(img)
        if err_msg or len(digit_arrays) == 0:
            return _error(err_msg or 'Không tìm thấy chữ số hợp lệ nào. Vui lòng kiểm tra lại hình ảnh.', 'preprocess')

        batch = np.stack(digit_arrays, axis=0)  # (n, 28, 28, 1)
        predictions = model.predict(batch, verbose=0)

        results = [_build_result(pred) for pred in predictions]

        # Kiểm tra độ tin cậy hậu suy luận (Post-inference confidence)
        confidences = [r['confidence'] for r in results]
        mean_conf = float(np.mean(confidences))
        low_conf_count = sum(1 for c in confidences if c < 0.55)

        if mean_conf < 0.65 or (low_conf_count / len(confidences)) >= 0.35:
            return _error(
                'Hệ thống không thể nhận diện rõ ràng các chữ số trong ảnh (độ tin cậy quá thấp). Vui lòng đảm bảo ảnh chụp dãy chữ số viết tay rõ ràng trên nền sạch.',
                'model',
                confidence=mean_conf,
            )

        number_string = ''.join(str(r['digit']) for r in results)
        return jsonify({
            'number': number_string,
            'digits': results,
            'results': results,
        })


@app.route('/predict-multi', methods=['POST'])
def predict_multi():
    """Dự đoán nhiều chữ số viết cạnh nhau, ghép thành 1 số hoàn chỉnh."""
    img, _mode, err = _read_image_from_request()
    if err:
        return err
    digit_arrays, err_msg = segment_multi_digits(img)

    if err_msg or len(digit_arrays) == 0:
        return _error(err_msg or 'Không tìm thấy chữ số nào', 'preprocess')

    batch = np.stack(digit_arrays, axis=0)  # (n, 28, 28, 1)
    predictions = model.predict(batch, verbose=0)

    results = [_build_result(pred) for pred in predictions]
    number_string = ''.join(str(r['digit']) for r in results)
    return jsonify({'number': number_string, 'digits': results})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


_MODEL_INFO_CACHE = None


@app.route('/model-info', methods=['GET'])
def model_info():
    """Thông tin bộ dữ liệu + kiến trúc CNN (đọc từ model đang chạy) để hiển thị trên web."""
    global _MODEL_INFO_CACHE
    if _MODEL_INFO_CACHE is None:
        _MODEL_INFO_CACHE = build_model_info(model)
    return jsonify(_MODEL_INFO_CACHE)


@app.route('/debug-segments', methods=['POST'])
def debug_segments():
    """Trả về số lượng chữ số tách được để debug."""
    img, _mode, err = _read_image_from_request()
    if err:
        return err
    digit_arrays_single, _ = segment_digits(img, merge_gap=10, dilate_iter=3)
    digit_arrays_multi, _  = segment_multi_digits(img)

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
