
from flask import Flask, render_template, redirect, url_for, request, Response
from search import search_bp
from img_search import img_search_bp, save_uploaded_file

# app = Flask(__name__, template_folder='E:\Python\搜索引擎实验\MyProject\Frontend\\templates')
app = Flask(__name__)
app.register_blueprint(search_bp)
app.register_blueprint(img_search_bp)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         return redirect(url_for('search.search', query=request.form['query'], page=1))
#     return render_template('index.html')  # 默认渲染 index.html 模板
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            # 保存上传的文件到指定目录，这里假设得到了文件名 filename
            filename = save_uploaded_file(request.files['file'])
            # 重定向到图像搜索页面，并传递文件名作为参数
            return redirect(url_for('img_search.img_rec', filename=filename))
        else:
            # 如果是普通的表单提交，执行文本搜索逻辑
            return redirect(url_for('search.search', query=request.form['query'], page=1))
    return render_template('index.html')  # 默认渲染 index.html 模板

if __name__ == '__main__':

    app.run(debug=True)



