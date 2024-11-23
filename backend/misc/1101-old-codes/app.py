from flask import Flask, jsonify, request, Response
import os
import subprocess
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all origins

@app.route('/generate', methods=['GET'])
def generate_article():
    query = request.args.get('query', 'default_topic')
    output_dir = f"generation_output_{query}"
    os.makedirs(output_dir, exist_ok=True)

    def generate():
        process = subprocess.Popen(
            ['python', 'main_script.py'], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True
        )

        for line in iter(process.stdout.readline, ''):
            yield f"data: {line}\n\n"
        process.stdout.close()
        process.wait()

    return Response(generate(), mimetype='text/event-stream')

@app.route('/article', methods=['GET'])
def get_article():
    try:
        # Use relative path to locate 'article.md' in the same directory
        file_path = 'article.md'
        print(f"Attempting to read file from: {file_path}")  # Debug file path

        with open(file_path, 'r', encoding='utf-8') as file:  # Specify utf-8 encoding
            content = file.read()
            print(f"File content:\n{content[:200]}")  # Print the first 200 characters

        return content, 200
    except Exception as e:
        print(f"Error reading article.md: {e}")  # Print error for debugging
        return str(e), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
