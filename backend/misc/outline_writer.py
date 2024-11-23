#outline writer
import anthropic
import json
import os
from glob import glob
from pathlib import Path

def read_file(file_path):
    """Read content from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_all_files_content(directory, extension='.txt'):
    """Get content from all files with given extension in a directory."""
    files = glob(os.path.join(directory, f'*{extension}'))
    content = []
    for file in files:
        content.append(read_file(file))
    return '\n\n'.join(content)

def get_source_files(directory):
    """Get content from all HTML files in the source directory."""
    files = glob(os.path.join(directory, '*.html'))
    sources = []
    for file in files:
        filename = os.path.basename(file)
        content = read_file(file)
        sources.append(f"File name: {filename}\nContent:\n{content}")
    return '\n\n---\n\n'.join(sources)

def generate_outline():
    # Read necessary files
    topic = read_file('topic.txt')
    user_profile = read_file(os.path.join('user_profile', 'User_Profile.txt'))
    style_guides = get_all_files_content('style_guide')
    source_materials = get_source_files('source_html')

    # Create the prompt with schema and example
    prompt = """You are an expert content outline generator. Please create an article outline based on the provided topic, source materials, and style guide.

Please provide your response in the following JSON schema. YOUR RESPONSE MUST BE A VALID JSON STRING THAT CAN BE PARSED BY json.loads():
{
    "topic": str,
    "style_guide": str,
    "sections": [
        {
            "section_title": str,
            "learning_goals": [str],
            "content_points": [
                {
                    "objective": str,
                    "content_summary": str,
                    "sources": [
                        {
                            "file_name": str,
                            "key_quote": str
                        }
                    ],
                    "image_wanted": str  # Optional. Leave empty string if no image needed. For needed images, provide keywords separated by forward slashes (/) that will be used to search Wikipedia Commons. Example: "Moment of inertia/spaceship/trains". Be specific, make sure image sticks to the specific content in this section.
                }
            ]
        }
    ]
}

Here's an example of a valid response:
{
    "topic": "Introduction to Neural Networks",
    "style_guide": "Use technical language but explain complex concepts with analogies. Include practical examples.",
    "sections": [
        {
            "section_title": "Basic Neural Network Architecture",
            "learning_goals": [
                "Understand the structure of a basic neural network"
            ],
            "content_points": [
                {
                    "objective": "Explain neural network layers",
                    "content_summary": "Cover input, hidden, and output layers",
                    "sources": [
                        {
                            "file_name": "basics.html",
                            "key_quote": "Neural networks consist of interconnected layers"
                        }
                    ],
                    "image_wanted": "Neural network architecture/deep learning/artificial intelligence"
                },
                {
                    "objective": "Describe activation functions",
                    "content_summary": "Explain common activation functions like ReLU and sigmoid",
                    "sources": [
                        {
                            "file_name": "basics.html",
                            "key_quote": "Activation functions determine the output of nodes"
                        }
                    ],
                    "image_wanted": ""  # No image needed for this section
                }
            ]
        }
    ]
}

Return ONLY the JSON output, with no additional text or explanation. Ensure your response is a valid JSON string that can be parsed using Python's json.loads(). For the image_wanted field, specify keywords separated by forward slashes (/) that will be used to search Wikipedia Commons, or leave it as an empty string if no image is needed for that section."""

    # Create the content prompt
    content_prompt = f"""Topic: {topic}

User Profile: {user_profile}

Style Guides:
{style_guides}

Source Materials:
{source_materials}

Based on the above information, generate a detailed article outline following the provided schema. Ensure all sources referenced exist in the provided materials. YOUR RESPONSE MUST BE A VALID JSON STRING."""

    # Initialize Anthropic client
    client = anthropic.Anthropic(
        api_key="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"
    )

    # Create message
    message = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=8000,
        temperature=0,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "user", "content": content_prompt}
        ]
    )

    response_text = message.content[0].text  # Get the text from the first content object

    # Parse the response
    try:
        outline = json.loads(response_text)
        
        # Save the outline to a JSON file
        output_path = "article_outline.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(outline, f, indent=2, ensure_ascii=False)
        
        print(f"Outline successfully generated and saved to {output_path}")
        return outline
    
    except json.JSONDecodeError as e:
        print("Error: Claude's response was not valid JSON")
        print("Saving response as text file instead...")
        
        # Save the raw response to a text file
        output_path = "article_outline.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(message.content)
        
        print(f"Raw response saved to {output_path}")
        print("Original error:", str(e))
        print("Response:", message.content)
        raise e

if __name__ == "__main__":
    try:
        outline = generate_outline()
    except Exception as e:
        print(f"Error generating outline: {str(e)}")