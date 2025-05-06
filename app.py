from flask import Flask, request, render_template, jsonify, url_for
import os
import google.generativeai as genai
import requests
import urllib.parse
from flask_sqlalchemy import SQLAlchemy

app = Flask("ReadBrief")

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Configure PostgreSQL from Render environment
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class BookSummary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    author = db.Column(db.String(256))
    summary = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(512))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    book_title = request.form.get('book_title')
    author = request.form.get('author', '')
    prompt = f"Summarize the book '{book_title}' by {author}."

    try:
        # 1. Get text summary from Gemini
        text_model = genai.GenerativeModel("models/gemini-2.0-flash")
        chat = text_model.start_chat()
        text_response = chat.send_message(prompt)
        summary = text_response.text

        # 2. Generate image using Pollinations AI
        combined_prompt = f"{book_title} book cover, cinematic, themes: {summary}"
        image_prompt = urllib.parse.quote(combined_prompt)
        params = {
            "width": 1280,
            "height": 720,
            "seed": 42,
            "model": "flux"
        }
        image_url = f"https://image.pollinations.ai/prompt/{image_prompt}"

        try:
            response = requests.get(image_url, params=params, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            image_url = url_for('static', filename='default_image.png')

        # 3. Save to PostgreSQL
        entry = BookSummary(
            title=book_title,
            author=author,
            summary=summary,
            image_url=image_url
        )
        db.session.add(entry)
        db.session.commit()

        recent_entries = BookSummary.query.order_by(BookSummary.id.desc()).limit(5).all()
        return render_template("result.html", title=book_title, author=author, summary=summary, image_url=image_url, recent_entries=recent_entries)

    except Exception as e:
        return render_template("result.html", title=book_title, author=author, summary=str(e), image_url=None)

@app.route('/initdb')
def initdb():
    try:
        db.create_all()
        return "✅ PostgreSQL tables created"
    except Exception as e:
        return f"❌ Error: {e}"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
