import os
import hashlib
import secrets
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, abort, jsonify
from werkzeug.utils import secure_filename
import markdown
import json

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['ARTICLES_FOLDER'] = 'docs'
app.config['ALLOWED_EXTENSIONS'] = {
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp',
    'mp4', 'webm', 'ogg', 'mov',
    'mp3', 'wav', 'ogg', 'm4a',
    'pdf', 'doc', 'docx', 'txt', 'md',
    'zip', 'rar', '7z'
}

# 确保文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['ARTICLES_FOLDER'], exist_ok=True)

# 管理员密码的SHA256哈希
ADMIN_PASSWORD_HASH = '7ea8aa746eaaa6dfbe7f1cde97c0ecca9afa204d071c487fb4f7debb5fcd301e'

def check_password(password):
    """检查密码是否正确"""
    return hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD_HASH

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_articles():
    """获取所有文章信息"""
    articles = []
    if os.path.exists('articles.json'):
        with open('articles.json', 'r', encoding='utf-8-sig') as f:
            articles = json.load(f)
    return articles

def save_articles(articles):
    """保存文章信息"""
    with open('articles.json', 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)

def generate_random_filename():
    """生成随机文件名"""
    return secrets.token_urlsafe(16)

# 提供CSS文件
@app.route('/css.css')
def serve_css():
    """提供css.css样式文件"""
    return send_from_directory('templates', 'css.css')

# 首页
@app.route('/')
def index():
    """首页显示所有文章"""
    articles = get_articles()
    articles.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return render_template('index.html', articles=articles)

@app.route('/docs/<path:filename>')
def show_article(filename):
    """显示文章内容"""
    article_path = os.path.join(app.config['ARTICLES_FOLDER'], filename)
    
    if not os.path.exists(article_path):
        abort(404)
    
    articles = get_articles()
    article_info = None
    for article in articles:
        if article.get('filename') == filename:
            article_info = article
            break
    
    if not article_info:
        abort(404)
    
    with open(article_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    html_content = markdown.markdown(content, extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.toc'
    ])
    
    return render_template('article.html', 
                         content=html_content,
                         title=article_info.get('title', '文章'),
                         created_at=article_info.get('created_at', ''),
                         author=article_info.get('author', '管理员'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    """管理员登录"""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if check_password(password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='密码错误')
    
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    """管理员仪表板"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    articles = get_articles()
    return render_template('admin.html', articles=articles)

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """提供上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/admin/logout')
def admin_logout():
    """退出登录"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin/create_article', methods=['POST'])
def create_article():
    """创建新文章"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': '未登录'}), 401
    
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    
    if not title or not content:
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    # 生成随机文件名
    filename = generate_random_filename() + '.md'
    article_path = os.path.join(app.config['ARTICLES_FOLDER'], filename)
    
    # 保存文章内容
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 保存文章信息
    articles = get_articles()
    articles.append({
        'id': len(articles) + 1,
        'title': title,
        'filename': filename,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'author': 'Dvs (DvsXT)'
    })
    save_articles(articles)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'message': '文章创建成功'
    })

@app.route('/admin/upload_file', methods=['POST'])
def upload_file():
    """上传文件"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': '未登录'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 添加时间戳避免重名
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{name}_{timestamp}{ext}"
        
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # 返回文件的URL
        file_url = url_for('uploaded_file', filename=filename, _external=True)
        return jsonify({
            'success': True,
            'url': file_url,
            'filename': filename
        })
    
    return jsonify({'error': '不支持的文件类型'}), 400

@app.route('/admin/delete_article', methods=['POST'])
def delete_article():
    """删除文章"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': '未登录'}), 401
    
    filename = request.form.get('filename', '').strip()
    if not filename:
        return jsonify({'error': '文件名不能为空'}), 400
    
    # 删除文章文件
    article_path = os.path.join(app.config['ARTICLES_FOLDER'], filename)
    if os.path.exists(article_path):
        os.remove(article_path)
    
    # 从文章中移除
    articles = get_articles()
    articles = [article for article in articles if article.get('filename') != filename]
    save_articles(articles)
    
    return jsonify({'success': True, 'message': '文章删除成功'})

if __name__ == '__main__':
    # 初始化articles.json文件
    if not os.path.exists('articles.json'):
        save_articles([])
    
    app.run(debug=False, port=50, host='0.0.0.0')