from flask import Flask, jsonify, request, Response
import os
import subprocess
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def run_script(script_name):
    process = subprocess.Popen(
        ['python', script_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    for line in iter(process.stdout.readline, ''):
        yield f"data: {line}\n\n"
    process.stdout.close()
    process.wait()

@app.route('/generate', methods=['GET'])
def generate_article():
    query = request.args.get('query', 'default_topic')
    output_dir = f"generation_output_{query}"
    os.makedirs(output_dir, exist_ok=True)

    def generate():
        # Generate article.md text version
        yield from run_script('main_script.py')
        yield "data: Text generation complete\n\n"
        
        # Notify frontend that image generation is starting
        yield "data: Image generation started\n\n"

        # Start image generation for updated_article.md
        yield from run_script('image_script.py')
        yield "data: Image generation complete\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/article', methods=['GET'])
def get_article():
    try:
        with open('article.md', 'r', encoding='utf-8') as file:
            content = file.read()
        return content, 200
    except Exception as e:
        return str(e), 500

@app.route('/updated_article', methods=['GET'])
def get_updated_article():
    try:
        if os.path.exists('updated_article.md'):
            with open('updated_article.md', 'r', encoding='utf-8') as file:
                content = file.read()
            return content, 200
        else:
            return "Not Ready", 202  # Accepted but not ready
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
