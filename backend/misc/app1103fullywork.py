from flask import Flask, jsonify, request, Response
import os
import subprocess
from flask_cors import CORS
import re
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Existing endpoint for generating articles
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
            check=True  # This will raise CalledProcessError if the script fails
        )

        # Try to parse the output as JSON
        try:
            response_data = json.loads(result.stdout)
            return jsonify({"status": "success", "data": response_data}), 200
        except json.JSONDecodeError:
            # Print stdout and stderr for debugging purposes
            print("Failed to parse JSON response.")
            print("Raw output (stdout):", result.stdout)
            print("Error output (stderr):", result.stderr)
            
            # If JSON parsing fails, return the raw output
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
    app.run(host='0.0.0.0', port=5000)
