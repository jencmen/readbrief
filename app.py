from flask import Flask, request, render_template, jsonify
import os
import google.generativeai as genai
import base64

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
        text_model = genai.GenerativeModel("gemini-2.0-flash")
        chat = text_model.start_chat()
        text_response = chat.send_message(prompt)
        summary = text_response.text

        # 2. Generate image from summary using gemini-pro-vision
        image_model = genai.GenerativeModel("models/gemini-pro-vision")
        image_prompt = f"Create a visually appealing, symbolic image that represents this book summary: {summary}"
        image_response = image_model.generate_content([image_prompt], generation_config={"response_mime_type": "image/png"})

        image_data = base64.b64encode(image_response.candidates[0].content.parts[0].raw_data).decode("utf-8")
        image_base64_url = f"data:image/png;base64,{image_data}"

        return render_template("result.html", title=book_title, author=author, summary=summary, image_url=image_base64_url)

    except Exception as e:
        return render_template("result.html", title=book_title, author=author, summary=str(e), image_url=None)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
