import os
import glob
import json
from datetime import datetime
from typing import List
from pydantic import BaseModel
from openai import OpenAI

class QuestionResponse(BaseModel):
    concept: str
    explanation: str

def load_text_files(directory: str) -> str:
    """Load all .txt files from a directory and concatenate their content."""
    content = []
    for file_path in glob.glob(os.path.join(directory, "*.txt")):
        with open(file_path, 'r', encoding='utf-8') as file:
            content.append(file.read())
    return "\n\n".join(content)

def load_markdown_file(file_path: str) -> str:
    """Load content from a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def save_response(response: QuestionResponse):
    """Save the response to a JSON file with timestamp and return the response."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Get the directory where feedback.py is located
    current_dir = os.path.dirname(__file__)
    # Define the responses directory relative to feedback.py's location
    responses_dir = os.path.join(current_dir, "responses")
    os.makedirs(responses_dir, exist_ok=True)
    
    output_path = os.path.join(responses_dir, f"response_{timestamp}.json")
    
    try:
        # Handle both Pydantic v1 and v2
        response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(response_dict, f, indent=2)
        
        # Print the response JSON to stdout for subprocess capture
        print(json.dumps(response_dict))
        return response_dict
    except Exception as e:
        error_msg = {"error": str(e)}
        print(json.dumps(error_msg))
        return error_msg

def parse_input_args(input_string: str) -> tuple:
    """Parse input string separated by '/' into components."""
    components = input_string.split('/')
    if len(components) != 4:
        raise ValueError("Input string must contain exactly 4 components separated by '/'")
    return components[0], components[1], components[2], components[3]

def generate_response(concept: str, context: str, user_comment: str, markdown_file: str) -> QuestionResponse:
    """Generate a response using OpenAI based on the provided context."""
    
    # Load all context files
    try:
        user_profiles = load_text_files("user_profile")
        style_guides = load_text_files("style_guide")
        markdown_content = load_markdown_file(markdown_file)
    except FileNotFoundError as e:
        print(f"Warning: Some context files could not be loaded: {e}")
        # Set empty string for missing files
        user_profiles = ""
        style_guides = ""
        markdown_content = ""
    
    # Create the system prompt
    system_prompt = f"""
    You are an AI tutor helping users understand concepts from a markdown document.
    
    Context from the markdown file:
    {markdown_content}
    
    User profiles for context:
    {user_profiles}
    
    Style guides to follow:
    {style_guides}
    
    The specific concept appears in this context from the original passage:
    {context}
    
    Please explain the concept based on the context provided in the markdown file,
    taking into account the user's profile and following the style guide. Remember to be brief!
    Focus particularly on how the concept is used in the provided context.
    """
    
    client = OpenAI(api_key="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")
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": system_prompt},
            {"role": "user", "content": f"I'm confused about the concept: {concept}\nContext where it appears: {context}\nHere's why I'm confused: {user_comment}"}
        ],
        response_format=QuestionResponse
    )
    
    # Parse the JSON response into QuestionResponse
    response_dict = json.loads(completion.choices[0].message.content)
    return QuestionResponse(**response_dict)

def main(input_string: str):
    """Main function to handle the Q&A process."""
    try:
        # Parse input string
        concept, context, user_comment, markdown_file = parse_input_args(input_string)
        
        # Generate response
        response = generate_response(concept, context, user_comment, markdown_file)
        
        # Save response and print JSON
        result = save_response(response)
        
        # No need for additional print statements that might interfere with JSON parsing
        return result
        
    except Exception as e:
        error_result = {"error": str(e)}
        print(json.dumps(error_result))
        return error_result

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate explanations for user questions')
    parser.add_argument('input_string', 
                      help='Input string in format: concept/context/comment/markdown_file')
    
    args = parser.parse_args()
    
    main(args.input_string)