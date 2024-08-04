from flask import Blueprint, render_template, request, redirect, url_for, send_file, Response
from werkzeug.utils import secure_filename
import os

from MyProject.ImageRec.img_regcognizer import get_result

UPLOAD_FOLDER = 'F:\\uplordimgs_fromPulse'  # 请替换为你的文件上传目录路径
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}  # 允许上传的文件类型
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 限制上传文件的最大大小，即16MB

img_search_bp = Blueprint('img_search', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        target_filename = 'target_img' + os.path.splitext(file.filename)[-1]  # 获取上传文件的扩展名
        target_path = os.path.join(UPLOAD_FOLDER, target_filename)

        # 如果目标文件存在，先删除
        if os.path.exists(target_path):
            os.remove(target_path)

        # 保存文件为固定名称
        file.save(target_path)
        return target_filename  # 返回重命名后的文件名作为保存后的标识符
    else:
        return None  # 如果文件不合法或保存失败，返回 None


@img_search_bp.route('/img_rec', methods=['GET'])
def img_rec():

    target_filename = request.args.get('filename')
    # 构建目标图像文件路径
    target_img = os.path.join(UPLOAD_FOLDER, target_filename)

    # 获取目标图像文件
    if os.path.exists(target_img):
        # 调用 get_result 函数获取搜索结果
        search_result = get_result(target_img)

    else:
        print("找不到目标图片")
        search_result = None

    # 渲染模板并传递数据
    return render_template('img_rec.html', target_file=target_img, search_result=search_result)

@img_search_bp.route('/show_image', methods=['GET'])
def show_image():
    img_path = request.args.get('path')
    return send_file(img_path, mimetype='image/jpg')  # 假设图片类型为 jpg，根据实际情况修改 mimetype
