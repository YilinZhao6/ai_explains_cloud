#!/usr/bin/env python3
from openai import OpenAI
import json
import os
from glob import glob
from pathlib import Path
from typing import List, Dict
from pydantic import BaseModel

# Set your OpenAI API key
client = OpenAI(api_key="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")

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

class SectionContent(BaseModel):
    section_title: str
    content: str

def write_section(
    section: Dict,
    context_files: Dict[str, str],
    previous_sections: str
) -> str:
    """Write a single section using OpenAI with structured output, and manually patch the section title."""
    
    # Get source files mentioned in this section
    source_files = set()
    for point in section['content_points']:
        for source in point['sources']:
            source_files.add(source['file_name'])
    
    # Create the prompt
    prompt = f"""You are writing one section of a larger educational article that helps the user to do self-learning. Here's the context:

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

IMPORTANT:
1. Follow the style guide strictly.
2. Address all learning goals and content points for the section.
3. Use the provided source materials as necessary.
4. Maintain consistency with previous sections.
5. You MUST not return images, links and diagrams of any form. For formulas, use LaTeX (without extra packages) syntax for Markdown.
6. Each section should limit subsections to 2 and avoid introduction or conclusion paragraphs.
7. In each section, please do not write introduction, conclusion, or summary. Limit the number of subsections in each section to 2.
8. For each content point, follow the "example_wanted" field. If it says "YES", add a relevant example; if "NO", skip the example. You should stick to the format below when adding examples:

<div class="example-box" style="clear: both;">

**Example: PUT YOUR TITLE HERE** # There must be a blank line between <div class="example-box"> and Example title

**Problem**: PUT YOUR QUESTION HERE.

**Solution**: PUT YOUR SOLUTION HERE.

</div>


9. If you are writing a section called related topics, please number at most 6 topics related to this passage that guides user to learn as next-steps. You MUST PUT the ## Related Topics inside <div style="clear: both;">...</div> You must format the content in the format below.

<div style="clear: both;">

## Related Topics

<div class="related-topics">

**Topic A**: Explanation of a related idea that provides additional context and enrichment.

**Topic B**: Explanation of a related idea that provides additional context and enrichment.

**Topic C**: Explanation of a related idea that provides additional context and enrichment.

... could list more here!

</div>

"""

    format_prompt = """
Math Formatting Requirements:
- Use $...$ for inline math
- Use $$...$$$ for display math (on separate lines)
- NEVER use \[...\] or \(...\) delimiters
- For aligned equations, use $$\begin{aligned}...\end{aligned}$$
- Always leave blank lines before and after display math blocks
- Must use \ before LaTeX commands, e.g. \frac, \begin{aligned}
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
    # Get response from OpenAI
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt},
            {"role": "user", "content": format_prompt}

        ],
        max_tokens=3000,
        temperature=0.1,
        response_format=SectionContent
    )
    
    if section['section_title'] == "Related Topics":
        section_content = response.choices[0].message.parsed.content
    else:
        section_content = f"## {section['section_title']}\n\n" + response.choices[0].message.parsed.content

    return section_content

def generate_article():
    """Generate the article from the outline, without introduction and conclusion."""
    try:
        # Read the outline
        with open('article_outline.json', 'r', encoding='utf-8') as f:
            outline = json.load(f)
        
        # Get context files
        context_files = get_context_files()
        
        # Initialize empty list for article sections
        article_sections = []
        
        # Write each section
        for section in outline['sections']:
            print(f"Writing section: {section['section_title']}".encode('utf-8').decode())
            
            # Get previously written content
            previous_sections = '\n\n'.join(article_sections)
            
            # Generate the section
            section_content = write_section(
                section=section,
                context_files=context_files,
                previous_sections=previous_sections
            )
            
            article_sections.append(section_content)
            print(f"Completed section: {section['section_title']}".encode('utf-8').decode())
        
        # Combine all sections
        full_article = '\n\n'.join(article_sections)
        
        # Save the article with UTF-8 encoding
        output_path = 'article.md'
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_article)
        
        print(f"Article successfully generated and saved to {output_path}".encode('utf-8').decode())
        return full_article
        
    except Exception as e:
        print(f"Error generating article: {str(e)}".encode('utf-8').decode())
        raise e

if __name__ == "__main__":
    try:
        generate_article()
    except Exception as e:
        print(f"Failed to generate article: {str(e)}")