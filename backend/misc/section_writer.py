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
9. The title of each section should be EXACTLY the same as the section title in outline
10. You must use KaTeX for mathematical expressions. Do not use [...] delimiters, use $ instead!!


Write ONLY the section content in Markdown format, starting with the section header (##)."""
    
    format_prompt = """
Math Formatting Requirements:
- Use $...$ for inline math
- Use $$...$$$ for display math (on separate lines)
- NEVER use \[...\] or \(...\) delimiters
- For aligned equations, use $$\begin{aligned}...\end{aligned}$$
- Always leave blank lines before and after display math blocks
You MUST USE KaTeX for mathematical expressions. Here are examples of correct formatting:
- Simple inline math: $E = mc^2$
- Block equation: 
  $$
  i\\hbar\\frac{\\partial}{\\partial t}\\Psi(r,t) = \\hat{H}\\Psi(r,t)
  $$
- Aligned equations:
  $$
  \\begin{aligned}
  \\nabla \\times E &= -\\frac{\\partial B}{\\partial t} \\\\
  \\nabla \\times B &= \\mu_0 J
  \\end{aligned}
  $$
- Some other examples:
$$
i\hbar \frac{\partial}{\partial t} \Psi(\mathbf{r}, t) = \left[ -\frac{\hbar^2}{2m} \nabla^2 + V(\mathbf{r}) \right] \Psi(\mathbf{r}, t)
$$
"""

    # Get response from Claude
    message = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=8000,
        temperature=0.1,
        messages=[
            {"role": "user", "content": prompt},
            {"role": "user", "content": format_prompt}

        ]
    )
    
    return message.content[0].text

def generate_article():
    """Generate the article from the outline, without introduction and conclusion."""
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
        
        # Initialize empty list for article sections
        article_sections = []
        
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