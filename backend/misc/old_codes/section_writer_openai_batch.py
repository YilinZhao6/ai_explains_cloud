from openai import OpenAI
import json
import os
from glob import glob
from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel

# Set your OpenAI API key
client = OpenAI(api_key="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")

#Pydantic Return Scheme:
class SectionContent(BaseModel):
    section_title: str
    content: str

def read_file(file_path: str) -> str:
    """Read content from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_context_files() -> Dict[str, str]:
    """Read the main context files."""
    return {
        'topic': read_file('topic.txt'),
        'user_profile': read_file(os.path.join('user_profile', 'User_Profile.txt')),
        'style_guide': '\n\n'.join([read_file(f) for f in glob(os.path.join('style_guide', '*.txt'))])
    }

def get_source_content(file_names: List[str]) -> str:
    """Get content from specified source files."""
    source_content = []
    for file_name in file_names:
        file_path = os.path.join('source_html', file_name)
        if os.path.exists(file_path):
            content = read_file(file_path)
            source_content.append(f"File name: {file_name}\nContent:\n{content}")
    return '\n\n---\n\n'.join(source_content)

class ArticleContent(BaseModel):
    article: str

def generate_full_article():
    """Generate the full article in one run and save it to article.md."""
    try:
        # Read the outline
        with open('article_outline.json', 'r', encoding='utf-8') as f:
            outline = json.load(f)
        
        # Get context files
        context_files = get_context_files()

        # Gather source files across all sections in the outline
        all_source_files = set()
        for section in outline['sections']:
            for point in section['content_points']:
                for source in point['sources']:
                    all_source_files.add(source['file_name'])
        
        # Create the prompt
        prompt = f"""You are writing an educational article that supports self-learning. Use the following context:

Topic: {context_files['topic']}

User Profile: {context_files['user_profile']}

Style Guide: {context_files['style_guide']}

Outline:
{json.dumps(outline, indent=2)}

Relevant Source Materials:
{get_source_content(list(all_source_files))}

Please write the full article in Markdown format, using these guidelines:
1. Follow the style guide strictly.
2. Address all learning goals and content points from each section in the outline.
3. Use the provided source materials as necessary.
4. Ensure the sections flow naturally, starting with the title for each.
5. Avoid redundancy between sections and provide relevant examples as needed.

Write ONLY the article content in Markdown format, starting with the section headers (##) as per the outline.
"""

        # Get response from OpenAI
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=8000,
            response_format=SectionContent
        )
        
        # Extract the article content
        full_article = response.choices[0].message.parsed.content

        # Save the article
        output_path = 'article.md'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_article)
        
        print(f"Article successfully generated and saved to {output_path}")
        return full_article
        
    except Exception as e:
        print(f"Error generating article: {str(e)}")
        raise e

if __name__ == "__main__":
    try:
        generate_full_article()
    except Exception as e:
        print(f"Failed to generate article: {str(e)}")
