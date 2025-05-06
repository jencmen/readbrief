from flask import Flask, request, render_template, jsonify, url_for
import os
import base64
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
        # 1. Get text summary from gemini-pro
        text_model = genai.GenerativeModel("models/gemini-2.0-flash")
        chat = text_model.start_chat()
        text_response = chat.send_message(prompt)
        summary = text_response.text

        # 2. Generate symbolic image from summary using gemini-vision (simulated image output)
        image_prompt = f"Create a symbolic illustration that visually represents the themes and story of: {summary}"
        vision_model = genai.GenerativeModel("models/gemini-1.0-pro-vision-latest")

        try:
            vision_response = vision_model.generate_content([
                image_prompt
            ], generation_config={"response_mime_type": "text/plain"})

            # NOTE: Gemini currently cannot return real image data, this is a placeholder
            # You would replace this with real image generation logic when supported
            image_placeholder = url_for('static', filename='default_image.png')
            image_url = image_placeholder

        except Exception as vision_error:
            image_url = url_for('static', filename='default_image.png')

        return render_template("result.html", title=book_title, author=author, summary=summary, image_url=image_url)

    except Exception as e:
        return render_template("result.html", title=book_title, author=author, summary=str(e), image_url=None)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
