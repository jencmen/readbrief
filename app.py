from flask import Flask, request, render_template, jsonify
import os
import google.generativeai as genai

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
        models = genai.list_models()
        # 1. Get text summary from gemini-pro
        text_model = genai.GenerativeModel("gemini-2.0-flash")
        chat = text_model.start_chat()
        text_response = chat.send_message(prompt)
        summary = text_response.text + models

        # 2. Use Unsplash for a symbolic book image
        image_url = f"https://source.unsplash.com/800x400/?book,{book_title.replace(' ', '+')}"

        return render_template("result.html", title=book_title, author=author, summary=summary, image_url=image_url)

    except Exception as e:
        return render_template("result.html", title=book_title, author=author, summary=str(e), image_url=None)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
