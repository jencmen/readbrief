from flask import Flask, request, render_template, jsonify
import os
import google.generativeai as genai

app = Flask("ReadBrief")

# Set your Google AI Studio API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Route for homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route for summarization API
@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    book_title = data.get('book_title')
    author = data.get('author', '')

    prompt = f"Summarize the book '{book_title}' by {author}."

    try:
        model = genai.GenerativeModel("models/gemini-pro")
        chat = model.start_chat()
        response = chat.send_message(prompt)
        summary = response.text
        return jsonify({'summary': summary})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
