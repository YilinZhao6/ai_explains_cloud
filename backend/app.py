from flask import Flask, jsonify, request, Response, send_from_directory
import os
import subprocess
from flask_cors import CORS
import re
import json
from datetime import datetime
import shutil
from time import sleep

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def clear_article_files():
    """Delete article.md, updated_article.md, and article_outline.json if they exist"""
    if os.path.exists('article.md'):
        os.remove('article.md')
    if os.path.exists('updated_article.md'):
        os.remove('updated_article.md')
    if os.path.exists('article_outline.json'):
        os.remove('article_outline.json')

def save_articles_to_archive(topic):
    """
    Save article.md and updated_article.md to a timestamped subfolder
    Returns the created directory path
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = f"data/{topic}_{timestamp}"
    
    # Create the data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Create the timestamped subfolder
    os.makedirs(dir_name, exist_ok=True)
    
    # Copy files if they exist
    if os.path.exists('article.md'):
        shutil.copy2('article.md', f"{dir_name}/article.md")
    if os.path.exists('updated_article.md'):
        shutil.copy2('updated_article.md', f"{dir_name}/updated_article.md")
    
    return dir_name

# Existing endpoint for generating articles
@app.route('/generate', methods=['GET'])
def generate_article():
    query = request.args.get('query', 'default_topic')
    
    # Clear existing article files before generating new ones
    clear_article_files()

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

# Endpoint to get the initial article
@app.route('/article', methods=['GET'])
def get_article():
    try:
        with open('article.md', 'r', encoding='utf-8') as file:
            content = file.read()
        return content, 200
    except Exception as e:
        return str(e), 500

# Endpoint to get the updated article with images
@app.route('/updated_article', methods=['GET'])
def get_updated_article():
    try:
        if os.path.exists('updated_article.md'):
            # Read the topic from topic.txt
            try:
                with open('topic.txt', 'r') as file:
                    topic = file.read().strip()
            except:
                topic = "default_topic"
            
            # Save files to archive
            archive_dir = save_articles_to_archive(topic)
            
            # Read and return the updated article content
            with open('updated_article.md', 'r', encoding='utf-8') as file:
                content = file.read()
            return content, 200
        else:
            return "Not Ready", 202  # Accepted but not ready
    except Exception as e:
        return str(e), 500

# Helper function to find the sentence containing the selected concept
def get_sentence_containing_concept(concept, file_path='article.md'):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        # Use regex to find the sentence containing the concept
        sentences = re.split(r'(?<=[.!?])\s+', content)  # Split content into sentences
        for sentence in sentences:
            if concept in sentence:
                return sentence.strip()
        return "Context not found in file"
    except FileNotFoundError:
        return "Markdown file not found"

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    concept = data.get('concept')
    user_comment = data.get('question')
    markdown_file = 'article.md'

    # Extract the context by finding the sentence with the selected concept
    context = get_sentence_containing_concept(concept, markdown_file)
    if context == "Markdown file not found" or context == "Context not found in file":
        return jsonify({"status": "error", "error": context}), 404

    # Construct the input argument string for feedback.py
    input_string = f"{concept or 'NULL'}/{context or 'NULL'}/{user_comment or 'NULL'}/{markdown_file}"
    print("Input string:", input_string)  # Debugging output

    try:
        # Run feedback.py with the formatted input string
        result = subprocess.run(
            ['python', 'feedback.py', input_string],
            capture_output=True,
            text=True,
            check=True
        )

        # Try to parse the output as JSON
        try:
            response_data = json.loads(result.stdout)
            return jsonify({"status": "success", "data": response_data}), 200
        except json.JSONDecodeError:
            print("Failed to parse JSON response.")
            print("Raw output (stdout):", result.stdout)
            print("Error output (stderr):", result.stderr)
            
            return jsonify({
                "status": "error",
                "error": "Failed to parse JSON response",
                "raw_output": result.stdout,
                "stderr": result.stderr
            }), 500

    except subprocess.CalledProcessError as e:
        return jsonify({
            "status": "error",
            "error": "Script execution failed",
            "stderr": e.stderr,
            "stdout": e.stdout
        }), 500
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500
    
@app.route('/save_query', methods=['POST'])
def save_query():
    data = request.json
    query = data.get('query', '')

    # Save the query to topic.txt
    with open('topic.txt', 'w') as file:
        file.write(query)
    
    return jsonify({"status": "success"}), 200

@app.route('/get-topic', methods=['GET'])
def get_topic():
    directory = os.path.dirname(__file__)  # Adjust the directory path as needed
    return send_from_directory(directory, 'topic.txt', mimetype='text/plain')

# New endpoint to check if article_outline.json exists
@app.route('/check_outline', methods=['GET'])
def check_outline():
    if os.path.exists('article_outline.json'):
        try:
            with open('article_outline.json', 'r') as file:
                data = json.load(file)
                sections = data.get('sections', [])
                if sections:
                    # Return all sections instead of just the first
                    return jsonify({"exists": True, "sections": sections})
                return jsonify({"exists": True, "sections": []})  # No sections found
        except Exception as e:
            return jsonify({"exists": False, "error": str(e)})
    return jsonify({"exists": False})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path and os.path.exists(f'frontend/dist/{path}'):  # Adjust path if using `.dist`
        return send_from_directory('frontend/dist', path)  # Adjust to `.dist` if needed
    else:
        return send_from_directory('frontend/dist', 'index.html')  # Serve the React app's entry point

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

if __name__ == "__main__":
    # Use the PORT environment variable provided by Render, default to 5000 for local testing
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)