from flask import Flask, request, jsonify
from flask_cors import CORS
from keras.models import load_model
import numpy as np
from PIL import Image
import base64
import io

from preprocessing import preprocess_image, segment_digits

app = Flask(__name__)
CORS(app)  # Cho phép Vue (chạy ở port khác) gọi API này

# Load model 1 lần duy nhất khi server khởi động
model = load_model('models/mnist_cnn_model.h5')
print("Model đã load thành công")


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
        predicted_digit = int(np.argmax(prediction))
        probabilities = {str(i): float(p) for i, p in enumerate(prediction[0])}
        return jsonify({
            'digit': predicted_digit,
            'probabilities': probabilities,
            'results': [{'digit': predicted_digit, 'probabilities': probabilities}]
        })
    else:
        digit_arrays = segment_digits(img)
        if len(digit_arrays) == 0:
            return jsonify({'error': 'Không tìm thấy chữ số nào'}), 400

        batch = np.stack(digit_arrays, axis=0)  # (n, 28, 28, 1)
        predictions = model.predict(batch)

        results = []
        for pred in predictions:
            predicted_digit = int(np.argmax(pred))
            probabilities = {str(i): float(p) for i, p in enumerate(pred)}
            results.append({
                'digit': predicted_digit,
                'confidence': float(np.max(pred)),
                'probabilities': probabilities
            })

        number_string = ''.join(str(r['digit']) for r in results)
        return jsonify({
            'number': number_string,
            'digits': results,
            'results': results
        })


@app.route('/predict-multi', methods=['POST'])
def predict_multi():
    """Dự đoán nhiều chữ số viết cạnh nhau, ghép thành 1 số hoàn chỉnh."""
    data = request.get_json()
    image_data = data.get('image')
    if not image_data:
        return jsonify({'error': 'Thiếu dữ liệu ảnh'}), 400

    img = decode_base64_image(image_data)
    digit_arrays = segment_digits(img)

    if len(digit_arrays) == 0:
        return jsonify({'error': 'Không tìm thấy chữ số nào'}), 400

    batch = np.stack(digit_arrays, axis=0)  # (n, 28, 28, 1)
    predictions = model.predict(batch)

    results = []
    for pred in predictions:
        digit = int(np.argmax(pred))
        confidence = float(np.max(pred))
        results.append({'digit': digit, 'confidence': confidence})

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
    digit_arrays = segment_digits(img)

    return jsonify({
        'so_luong_tach_duoc': len(digit_arrays),
        'ghi_chu': 'Nếu số này khác với số chữ số bạn thực sự vẽ, cần chỉnh merge_gap trong preprocessing.py'
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
