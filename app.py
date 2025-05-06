from flask import Flask, request, render_template, jsonify, url_for
import os
import google.generativeai as genai
import requests

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

        # 2. Get an image from Unsplash
        try:
            headers = {
                "Accept-Version": "v1",
                "Authorization": f"Client-ID {os.getenv('UNSPLASH_ACCESS_KEY')}"
            }
            query = f"{book_title} book"
            response = requests.get(
                "https://api.unsplash.com/search/photos",
                params={"query": query, "per_page": 1},
                headers=headers
            )
            response.raise_for_status()

            results = response.json()
            if results["results"]:
                image_url = results["results"][0]["urls"]["regular"]
            else:
                image_url = url_for('static', filename='default_image.png')

        except Exception as unsplash_error:
            image_url = url_for('static', filename='default_image.png')

        return render_template("result.html", title=book_title, author=author, summary=summary, image_url=image_url)

    except Exception as e:
        return render_template("result.html", title=book_title, author=author, summary=str(e), image_url=None)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
