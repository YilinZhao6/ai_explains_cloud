from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
import json
import subprocess
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')  # For Python 3.7+


class ImageSearchCommand(BaseModel):
    command: str = Field(description="The full command to execute image retrieval script")

def read_outline(file_path: str = "article_outline.json") -> dict:
    """Read the article outline JSON file."""
    print("\n📖 Reading article outline...")
    with open(file_path, 'r', encoding='utf-8') as f:
        outline = json.load(f)
        print("✅ Successfully loaded article outline")
        return outline

def analyze_image_requirements(outline_data: dict) -> List[dict]:
    """Extract and process image requirements from the outline."""
    print("\n🔍 Analyzing image requirements from outline...")
    image_requests = []
    
    for section in outline_data.get("sections", []):
        section_title = section.get("section_title", "")
        for point in section.get("content_points", []):
            image_wanted = point.get("image_wanted", "").strip()
            if image_wanted:
                image_requests.append({
                    "keywords": image_wanted,
                    "section": section_title,
                    "objective": point.get("objective", ""),
                    "content_summary": point.get("content_summary", "")
                })
    
    print(f"✅ Found {len(image_requests)} image requests in the outline")
    return image_requests

def generate_search_command(image_requests: List[dict], outline_data: dict) -> str:
    print("\n🤖 Generating optimized search command using GPT-4...")
    
    prompt = f"""As an AI image search optimizer, analyze this article outline and its image requirements:

ARTICLE TOPIC: {outline_data.get('topic', '')}

OUTLINE AND IMAGE REQUESTS:
{json.dumps(image_requests, indent=2)}

Generate a single command for image_retrieval_command_args.py to search for images on Wikipedia Commons.

Guidelines:
1. Default is 3 images per keyword unless context suggests otherwise
2. Analyze the section context and objective to remove redundant keywords
3. Combine similar searches to avoid duplicates
4. Only keep keywords that are truly relevant and specific to the educational content
5. Format: python image_retrieval_command_args.py "keyword1:limit" "keyword2:limit"

Return ONLY the command string that will be executed."""

    client = OpenAI(api_key="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")
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI that optimizes image search commands based on educational content needs."},
            {"role": "user", "content": prompt}
        ],
        response_format=ImageSearchCommand,
    )
    
    command = completion.choices[0].message.parsed.command
    print("✅ Search command generated successfully")
    return command

def execute_command(command: str):
    """Execute the generated command."""
    print("\n🚀 Executing image search and download command...")
    print(f"Command: {command}\n")
    
    try:
        subprocess.run(command, shell=True, check=True)
        print("✅ Successfully completed image downloads")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing command: {e}")

def main():
    try:
        # Read the article outline
        outline = read_outline()
        
        # Extract image requirements with context
        image_requests = analyze_image_requirements(outline)
        
        if not image_requests:
            print("❌ No image requirements found in the outline.")
            return
        
        # Generate the search command
        command = generate_search_command(image_requests, outline)
        
        # Execute the command
        execute_command(command)
        
        print("\n✨ Image processing completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🎯 Starting Image Requirement Processor")
    main()