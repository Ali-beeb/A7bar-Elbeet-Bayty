import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# إعداد التطبيق وقاعدة البيانات
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ده نموذج (Model) بيمثل جدول الأخبار في قاعدة البيانات
class NewsItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# دي صفحة الموقع الرئيسية اللي بتعرض الأخبار
@app.route('/')
def home():
    news_items = NewsItem.query.order_by(NewsItem.timestamp.desc()).all()
    return render_template('index.html', news=news_items)

# دي نقطة الاتصال (API) اللي أنا هستخدمها لإضافة الأخبار
@app.route('/api/add-news', methods=['POST'])
def add_news():
    # التحقق من المفتاح السري للتأكد إني أنا اللي ببعت الخبر
    secret_key = request.headers.get('X-Api-Key')
    if secret_key != app.config['SECRET_KEY']:
        return jsonify({"error": "Unauthorized"}), 401
    
    # الحصول على بيانات الخبر من الطلب
    data = request.json
    title = data.get('title')
    content = data.get('content')
    
    # التأكد إن العنوان والمحتوى مش فاضيين
    if not title or not content:
        return jsonify({"error": "Missing title or content"}), 400
    
    # إضافة الخبر لقاعدة البيانات
    new_item = NewsItem(title=title, content=content)
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({"message": "News added successfully!"}), 201

# ده هيعمل قاعدة البيانات ويضيف أول خبر تجريبي لو مش موجود
def setup_database():
    with app.app_context():
        db.create_all()
        # إضافة أول خبر لو قاعدة البيانات فاضية
        if not NewsItem.query.first():
            first_news = NewsItem(title='أخبار البيت بيتي 3', content='مرحبا بك في الموقع. سيتم تحديث الأخبار هنا.')
            db.session.add(first_news)
            db.session.commit()
            print("تم إنشاء قاعدة البيانات وإضافة أول خبر بنجاح!")

# الكود ده بيشغل الموقع
if __name__ == '__main__':
    setup_database()

    app.run(debug=True)

