import os
import cv2
import numpy as np
from keras.applications.resnet50 import ResNet50, preprocess_input

base_path = "datasets/images_2"
output_path = "datasets/features"  # 新目录的路径

def extract_features():
    w, h = 224, 224
    encoder = ResNet50(include_top=False)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    files = [file for file in os.listdir(base_path) if file.endswith(('png', 'jpg', 'jpeg'))]

    for file in files:
        img_path = os.path.join(base_path, file)
        img = cv2.resize(cv2.imread(img_path), (w, h))
        if isinstance(img, np.ndarray):
            img_features = encoder(preprocess_input(img[None]))
            np.save(os.path.join(output_path, f"{os.path.splitext(file)[0]}.npy"), img_features)

if __name__ == "__main__":
    extract_features()
    print("特征值提取完毕!")

