from flask import Flask, jsonify, request
import os
import subprocess
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This should come after the app is defined

@app.route('/generate', methods=['POST'])
def generate_article():
    query = request.json.get('query', 'default_topic')
    output_dir = f"generation_output_{query}"
    os.makedirs(output_dir, exist_ok=True)

    # Simulate running the original `main_script.py`
    result = subprocess.run(
        ['python', 'main_script.py'], capture_output=True, text=True
    )
    log_output = result.stdout

    # Parse output
    if "Extracting content from relevant URLs..." in log_output:
        print("Content extraction started...")
    if "Outline successfully generated and saved to article_outline.json" in log_output:
        print("Outline generated!")
    if "Article successfully generated and saved to article.md" in log_output:
        print("Article saved!")

    # Load generated article content
    article_path = os.path.join('article.md')
    if os.path.exists(article_path):
        with open(article_path, 'r', encoding='utf-8') as file:
            article_content = file.read()
    else:
        article_content = "No article generated."

    return jsonify({'article': article_content, 'log': log_output})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
