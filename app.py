from flask import Flask, request, render_template, jsonify, url_for
import os
import google.generativeai as genai
import requests
import urllib.parse

app = Flask("ReadBrief")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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

        # 2. Generate image using Pollinations API with summary included in prompt
        combined_prompt = f"{book_title} book cover, cinematic, themes: {summary}"
        image_prompt = urllib.parse.quote(combined_prompt)
        params = {
            "width": 1280,
            "height": 720,
            "seed": 42,
            "model": "flux"
        }
        image_url = f"https://image.pollinations.ai/prompt/{image_prompt}"

        # Optional: Validate the image URL by requesting it (fallback to default if fails)
        try:
            response = requests.get(image_url, params=params, timeout=60)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            image_url = url_for('static', filename='default_image.png')

        return render_template("result.html", title=book_title, author=author, summary=summary, image_url=image_url)

    except Exception as e:
        return render_template("result.html", title=book_title, author=author, summary=str(e), image_url=None)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
