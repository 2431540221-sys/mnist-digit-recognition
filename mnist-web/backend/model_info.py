"""
Thông tin về dữ liệu huấn luyện và kiến trúc CNN, trả về cho frontend qua GET /model-info.

- Phần KIẾN TRÚC được đọc trực tiếp từ model đã load (không gõ tay) nên luôn khớp file .h5.
- Phần DỮ LIỆU / HUẤN LUYỆN là hằng số, phải khớp với mnist_train.py ở thư mục gốc.
"""

# Khớp với mnist_train.py
DATASET_INFO = {
    'name': 'MNIST (Modified NIST)',
    'source': 'Yann LeCun et al. (từ bộ chữ số viết tay của NIST) — nạp bằng tensorflow.keras.datasets.mnist',
    'data_type': 'Hình ảnh (ảnh xám 28×28 px, giá trị 0–255) — không phải dữ liệu text',
    'preprocessing': 'Chia 255 để chuẩn hóa về [0, 1], reshape (28, 28, 1), nhãn one-hot 10 chiều',
    'total_samples': 70000,
    'train_samples': 60000,
    'validation_samples': 10000,
    'num_classes': 10,
    'classes': '0, 1, 2, 3, 4, 5, 6, 7, 8, 9',
    'split_note': (
        'Tập validation dùng trong lúc huấn luyện chính là 10.000 mẫu test chuẩn của MNIST '
        '(60.000 train / 10.000 validation).'
    ),
}

TRAINING_INFO = {
    'optimizer': 'Adam (learning rate = 0.001)',
    'loss': 'categorical_crossentropy',
    'batch_size': 128,
    'max_epochs': 25,
    'augmentation': 'Xoay ±12°, dịch ngang/dọc ±10%, zoom ±10%, shear ±10% (điền viền màu đen)',
    'callbacks': 'ModelCheckpoint (lưu model val_accuracy tốt nhất), ReduceLROnPlateau, EarlyStopping (patience = 5)',
}

_LAYER_LABELS = {
    'Conv2D': 'Tích chập 2D (Conv2D)',
    'BatchNormalization': 'Chuẩn hóa batch (BatchNorm)',
    'MaxPooling2D': 'Gộp cực đại (MaxPooling2D)',
    'Dropout': 'Dropout',
    'Flatten': 'Làm phẳng (Flatten)',
    'Dense': 'Kết nối đầy đủ (Dense)',
}


def _shape_str(shape):
    return '×'.join(str(d) for d in shape[1:])


def _describe_layer(layer):
    kind = type(layer).__name__
    cfg = layer.get_config()
    activation = cfg.get('activation')
    detail = ''
    if kind == 'Conv2D':
        k = cfg['kernel_size']
        detail = f"{cfg['filters']} bộ lọc · kernel {k[0]}×{k[1]} · stride {cfg['strides'][0]} · padding {cfg['padding']}"
    elif kind == 'MaxPooling2D':
        p = cfg['pool_size']
        detail = f'cửa sổ {p[0]}×{p[1]} · giảm một nửa kích thước ảnh'
    elif kind == 'Dropout':
        detail = f"tắt ngẫu nhiên {int(cfg['rate'] * 100)}% nơ-ron khi huấn luyện"
    elif kind == 'Dense':
        detail = f"{cfg['units']} nơ-ron"
    elif kind == 'BatchNormalization':
        detail = 'chuẩn hóa đầu ra lớp trước'
    elif kind == 'Flatten':
        detail = 'duỗi feature map thành vector 1 chiều'
    return {
        'name': layer.name,
        'type': kind,
        'label': _LAYER_LABELS.get(kind, kind),
        'output_shape': _shape_str(layer.output.shape),
        'params': int(layer.count_params()),
        'detail': detail,
        'activation': activation if activation and activation != 'linear' else None,
    }


def build_model_info(model):
    layers = [_describe_layer(l) for l in model.layers]
    counts = {}
    for l in layers:
        counts[l['type']] = counts.get(l['type'], 0) + 1
    trainable = int(sum(int(w.shape.num_elements()) for w in model.trainable_weights))
    non_trainable = int(sum(int(w.shape.num_elements()) for w in model.non_trainable_weights))
    return {
        'dataset': DATASET_INFO,
        'training': TRAINING_INFO,
        'model': {
            'input_shape': _shape_str(model.input_shape),
            'output_shape': _shape_str(model.output_shape),
            'total_layers': len(layers),
            'layer_counts': counts,
            'total_params': trainable + non_trainable,
            'trainable_params': trainable,
            'non_trainable_params': non_trainable,
            'layers': layers,
        },
    }
