from flask import Flask, jsonify, request, render_template
from llmchat.pdf_search_ollama import rag_query, clear_chat, process_pdf

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('chat.html')

@app.route('/ui/upload')
def upload():
    return render_template('upload.html')

@app.route('/app/chat', methods=['POST'])
def chat():
    data = request.get_json()
    return rag_query(data['message'])


@app.route('/app/clear')
def clear():
    clear_chat()
    return jsonify(message="Chat cleared!")

@app.route('/app/uploadrefresh', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are allowed'}), 400

    return process_pdf(file)

if __name__ == '__main__':
     app.run(debug=True)
