#!/usr/bin/env python3
from pydantic import BaseModel
from typing import List, Optional
from openai import OpenAI
import json
import os
from glob import glob
from pathlib import Path

# Pydantic models for structured output
class Source(BaseModel):
    file_name: str
    key_quote: str

class ContentPoint(BaseModel):
    objective: str
    content_summary: str
    sources: List[Source]
    example_wanted: str  # Removed default Field parameter

class Section(BaseModel):
    section_title: str
    learning_goals: List[str]
    content_points: List[ContentPoint]

class ArticleOutline(BaseModel):
    topic: str
    style_guide: str
    sections: List[Section]

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

    # Create the system prompt
    system_prompt = """You are an expert content outline generator. Create an article outline based on the provided topic, source materials, and style guide. 
    Your response must follow the specified schema with sections, learning goals, content points, and sources. For example_wanted, you can only put YES in at 1-2 sections! In other situations, put NO.
    
    The last section of the outline should always be Related Topics! You don't need to specify anything here. You should only return this:
    "section_title": "Related Topics",
    "learning_goals": [],
    "content_points": []
    """

    # Create the content prompt
    content_prompt = f"""Topic: {topic}

User Profile: {user_profile}

Style Guides:
{style_guides}

Source Materials:
{source_materials}

Based on the above information, generate a detailed article outline. Ensure all sources referenced exist in the provided materials."""

    # Initialize OpenAI client with your API key
    client = OpenAI(
        api_key="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"
    )

    completion = None
    try:
        # Create completion with structured output
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content_prompt}
            ],
            response_format=ArticleOutline,
        )

        # Get the parsed response directly
        outline = completion.choices[0].message.parsed
        
        # Save the outline to a JSON file
        output_path = "article_outline.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(outline.json(indent=2))
        
        print(f"Outline successfully generated and saved to {output_path}")
        return outline
    
    except Exception as e:
        print("Error generating outline")
        print("Original error:", str(e))
        
        # Save the raw response to a text file if there's an error
        if completion and hasattr(completion.choices[0].message, 'content'):
            output_path = "article_outline.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(str(completion.choices[0].message.content))
            print(f"Raw response saved to {output_path}")
        
        raise e

if __name__ == "__main__":
    try:
        outline = generate_outline()
    except Exception as e:
        print(f"Error generating outline: {str(e)}")