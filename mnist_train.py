import os
import keras
from keras.datasets import mnist
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.optimizers import Adam
from keras.preprocessing.image import ImageDataGenerator

# Tạo thư mục lưu model nếu chưa có
os.makedirs('models', exist_ok=True)

# 1. Tải dữ liệu MNIST
(X_train, y_train), (X_test, y_test) = mnist.load_data()
print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)

# 2. Tiền xử lý dữ liệu
X_train = X_train.reshape(X_train.shape[0], 28, 28, 1).astype('float32') / 255
X_test = X_test.reshape(X_test.shape[0], 28, 28, 1).astype('float32') / 255
input_shape = (28, 28, 1)
y_train = keras.utils.to_categorical(y_train, 10)
y_test = keras.utils.to_categorical(y_test, 10)

print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)

batchSize = 128
numClasses = 10
epochs = 20  # Tăng epochs để bù lại augmentation

# 3. Data Augmentation — giúp model chịu được chữ viết nghiêng, thu nhỏ, dịch chuyển
datagen = ImageDataGenerator(
    rotation_range=15,       # Xoay ngẫu nhiên ±15 độ
    zoom_range=0.1,          # Zoom in/out ±10%
    width_shift_range=0.1,   # Dịch ngang ±10%
    height_shift_range=0.1,  # Dịch dọc ±10%
    shear_range=0.1,         # Biến dạng nghiêng nhẹ
)
datagen.fit(X_train)

# 4. Xây dựng mô hình CNN (thêm 1 Conv layer để học được pattern phức tạp hơn)
model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=input_shape, padding='same'))
model.add(Conv2D(32, (3, 3), activation='relu', padding='same'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(numClasses, activation='softmax'))

# 5. Compile
model.compile(
    loss=keras.losses.categorical_crossentropy,
    optimizer=Adam(learning_rate=0.001),
    metrics=['accuracy']
)

# 6. Train với augmented data
print("Bắt đầu train với Data Augmentation...")
model.fit(
    datagen.flow(X_train, y_train, batch_size=batchSize),
    steps_per_epoch=len(X_train) // batchSize,
    epochs=epochs,
    verbose=1,
    validation_data=(X_test, y_test)
)

# 7. Đánh giá mô hình
score = model.evaluate(X_test, y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

# 8. Lưu model
model.save('models/mnist_cnn_model.h5')
print("Đã lưu model vào models/mnist_cnn_model.h5")
