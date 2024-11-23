import anthropic
import json
import os
from glob import glob
from pathlib import Path
from typing import List, Dict

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

def write_section(
    section: Dict,
    context_files: Dict[str, str],
    previous_sections: str,
    client: anthropic.Anthropic
) -> str:
    """Write a single section using Claude."""
    
    # Get source files mentioned in this section
    source_files = set()
    for point in section['content_points']:
        for source in point['sources']:
            source_files.add(source['file_name'])
    
    # Create the prompt
    prompt = f"""You are writing one section of an larger educational article that helps the user to do self-learning. Here's the context:

Topic: {context_files['topic']}

User Profile: {context_files['user_profile']}

Style Guide: {context_files['style_guide']}

Section Information:
Title: {section['section_title']}
Learning Goals: {', '.join(section['learning_goals'])}

Content Points to Cover:
{json.dumps(section['content_points'], indent=2)}

Previously Written Sections:
{previous_sections if previous_sections else "No previous sections yet."}

Relevant Source Materials:
{get_source_content(list(source_files))}

Please write this section following these guidelines:
1. Follow the style guide strictly
2. Address all learning goals
3. Cover all content points
4. Use the provided source materials
5. Maintain consistency with previous sections
6. Use Markdown formatting for headings and text structure
7. Avoid repeating information from previous sections
8. Include relevant examples and explanations

Write ONLY the section content in Markdown format, starting with the section header (##)."""

    # Get response from Claude
    message = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=8000,
        temperature=0,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text

def generate_article():
    """Generate the complete article from the outline."""
    try:
        # Initialize Anthropic client
        client = anthropic.Anthropic(
            api_key="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"
        )
        
        # Read the outline
        with open('article_outline.json', 'r', encoding='utf-8') as f:
            outline = json.load(f)
        
        # Get context files
        context_files = get_context_files()
        
        # Generate article title and introduction
        intro_prompt = f"""Write an introduction for an article with the following details:

Topic: {context_files['topic']}
Style Guide: {context_files['style_guide']}
User Profile: {context_files['user_profile']}

Write a title and introduction in Markdown format. Use # for the title and write a compelling introduction that sets up the article."""

        intro_message = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=1000,
            temperature=0,
            messages=[{"role": "user", "content": intro_prompt}]
        )
        
        # Start with the introduction
        article_sections = [intro_message.content[0].text]
        
        # Write each section
        for section in outline['sections']:
            print(f"Writing section: {section['section_title']}")
            
            # Get previously written content
            previous_sections = '\n\n'.join(article_sections)
            
            # Generate the section
            section_content = write_section(
                section=section,
                context_files=context_files,
                previous_sections=previous_sections,
                client=client
            )
            
            article_sections.append(section_content)
            print(f"Completed section: {section['section_title']}")
        
        # Generate conclusion
        conclusion_prompt = f"""Write a conclusion for the following article:

{article_sections[-1]}

Previous sections have covered: {', '.join(s['section_title'] for s in outline['sections'])}

Write a conclusion that summarizes the key points and provides a strong ending. Use Markdown format with ## Conclusion as the header."""

        conclusion_message = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=1000,
            temperature=0,
            messages=[{"role": "user", "content": conclusion_prompt}]
        )
        
        # Add conclusion
        article_sections.append(conclusion_message.content[0].text)
        
        # Combine all sections
        full_article = '\n\n'.join(article_sections)
        
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
        generate_article()
    except Exception as e:
        print(f"Failed to generate article: {str(e)}")