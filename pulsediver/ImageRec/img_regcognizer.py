import os
import shutil
import time

import cv2
import numpy as np
from keras.applications.resnet50 import ResNet50, preprocess_input

base_path = r'E:\Python\搜索引擎实验\MyProject\ImageRec\datasets\images_2'
features_path = r'E:\Python\搜索引擎实验\MyProject\ImageRec\datasets\features'
result_folder = r'E:\Python\搜索引擎实验\MyProject\ImageRec\datasets\result'

def keras_resnet50(target_path):
    w, h = 224, 224
    encoder = ResNet50(include_top=False)

    target = cv2.resize(cv2.imread(target_path), (w, h))
    target = encoder(preprocess_input(target[None]))

    distances = []
    feature_files = [file for file in os.listdir(features_path) if file.endswith('.npy')]

    for file in feature_files:
        feature = np.load(os.path.join(features_path, file))
        distance = np.sum((target - feature) ** 2)
        distances.append((file, distance))

    distances = sorted(distances, key=lambda x: x[1])[:15]
    return distances

# def copy_similar_images(distances):
#     if not os.path.exists(result_folder):
#         os.makedirs(result_folder)
#
#     for i, (file, _) in enumerate(distances, start=1):
#         img_name = os.path.splitext(file)[0]
#         img_path = os.path.join(base_path, f"{img_name}.jpg")
#         print(f"Similar image {i}: {img_path}")  # 打印相似图片的位置
#         img = cv2.imread(img_path)
#         if isinstance(img, np.ndarray):
#             img = img.copy()
#             cv2.imwrite(f"{result_folder}/result{i}.jpg", img)
#


def copy_similar_images(distances):
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    for i, (file, _) in enumerate(distances, start=1):
        img_name = os.path.splitext(file)[0]
        img_path = os.path.join(base_path, f"{img_name}.jpg")
        print(f"Similar image {i}: {img_path}")  # 打印相似图片的位置

        # 构建目标文件路径
        target_file_path = os.path.join(result_folder, f"result{i}.jpg")

        try:
            shutil.copyfile(img_path, target_file_path)  # 复制文件
        except FileNotFoundError as e:
            print(f"Error: {e}")

def get_all_images(folder):
    # 获取指定文件夹中的所有图片文件路径
    all_images = [os.path.join(folder, file) for file in os.listdir(folder) if
                  file.lower().endswith(('.png', '.jpg', '.jpeg'))]
    return all_images

#调用此函数得到结果
def get_result(target_file):
    similar_images = keras_resnet50(target_file)
    copy_similar_images(similar_images)
    return get_all_images(result_folder)

if __name__ == "__main__":
    target_path = "datasets/images_3/557.jpg"  # 你的目标图片路径
    start_time = time.time()
    similar_images = keras_resnet50(target_path)
    copy_similar_images(similar_images)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"用时：{execution_time}s")