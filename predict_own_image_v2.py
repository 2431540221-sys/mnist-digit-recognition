import os
from keras.models import load_model
import numpy as np
from PIL import Image
import sys

MODEL_PATH = 'models/mnist_cnn_model.h5'
IMAGES_DIR = 'images'
OUTPUTS_DIR = 'outputs'


def preprocess_image(image_path):
    # 1. Đọc ảnh, chuyển sang ảnh xám
    img = Image.open(image_path).convert('L')
    img_array = np.array(img)

    # 2. Tự động phát hiện nền: nếu nền sáng (trắng) thì đảo màu
    corners_mean = np.mean([
        img_array[0, 0], img_array[0, -1],
        img_array[-1, 0], img_array[-1, -1]
    ])
    if corners_mean > 127:
        img_array = 255 - img_array

    # 3. Threshold để loại bỏ nhiễu mờ
    img_array = np.where(img_array > 50, img_array, 0)

    # 4. Tìm bounding box của chữ số
    coords = np.argwhere(img_array > 30)
    if coords.size == 0:
        raise ValueError("Không tìm thấy nét vẽ nào trong ảnh, kiểm tra lại ảnh đầu vào")

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0) + 1

    # 5. Crop sát vào vùng chữ số
    digit = img_array[y0:y1, x0:x1]
    digit_img = Image.fromarray(digit)

    # 6. Resize giữ tỉ lệ khung hình về tối đa 20x20
    h, w = digit.shape
    if h > w:
        new_h = 20
        new_w = max(1, int(w * 20 / h))
    else:
        new_w = 20
        new_h = max(1, int(h * 20 / w))
    digit_img = digit_img.resize((new_w, new_h))

    # 7. Đặt vào giữa khung 28x28
    canvas = Image.new('L', (28, 28), color=0)
    upper_left = ((28 - new_w) // 2, (28 - new_h) // 2)
    canvas.paste(digit_img, upper_left)

    # 8. Lưu ảnh debug vào thư mục outputs
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    debug_path = os.path.join(OUTPUTS_DIR, f'{base_name}_processed.png')
    canvas.save(debug_path)
    print(f"Đã lưu ảnh sau xử lý vào {debug_path}")

    # 9. Chuẩn hóa dữ liệu
    final_array = np.array(canvas).astype('float32') / 255
    final_array = final_array.reshape(1, 28, 28, 1)
    return final_array


def predict_digit(image_path):
    model = load_model(MODEL_PATH)
    img_array = preprocess_image(image_path)

    prediction = model.predict(img_array)
    predicted_digit = np.argmax(prediction)
    confidence = np.max(prediction) * 100

    print(f"\nModel đoán đây là số: {predicted_digit} (độ tin cậy: {confidence:.2f}%)")
    print("\nXác suất chi tiết:")
    for digit, prob in enumerate(prediction[0]):
        print(f"  Số {digit}: {prob*100:.2f}%")

    return predicted_digit


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Cách dùng: python predict_own_image_v2.py ten_anh.png")
        print(f"Lưu ý: đặt ảnh vào thư mục '{IMAGES_DIR}/' rồi chỉ cần gõ tên file")
        print(f"Ví dụ: python predict_own_image_v2.py {IMAGES_DIR}/so3.png")
    else:
        image_path = sys.argv[1]
        predict_digit(image_path)
