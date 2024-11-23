from pydantic import BaseModel, Field
from typing import List, Dict
import json
import sys
import re
from pathlib import Path
from openai import OpenAI

sys.stdout.reconfigure(encoding='utf-8')

class FormattedSection(BaseModel):
    section_title: str
    formatted_content: str = Field(description="Markdown formatted content with integrated images")

def read_article(file_path: str = "article.md") -> str:
    """Read the article content."""
    print("\n📄 Reading article content...")
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_outline(file_path: str = "article_outline.json") -> dict:
    """Read the article outline."""
    print("\n📑 Reading article outline...")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def read_selected_images() -> Dict:
    """Read the selected images from JSON."""
    print("\n📸 Reading selected images...")
    with open("selected_images.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def format_section_with_images(section_title: str, section_content: str, section_images: List[Dict]) -> str:
    """Format a single section with its images."""
    prompt = f"""Add images to this article section WITHOUT modifying the original text:

Section Title: {section_title}

Original Content (DO NOT MODIFY THIS TEXT):
{section_content}

Available Images to Insert:
{json.dumps(section_images, indent=2)}

Guidelines:
1. KEEP ALL ORIGINAL TEXT EXACTLY AS IS - Do not change any wording, formatting, or structure
2. Only add image elements next to relevant paragraphs
3. For each image:
   - Convert its path to start with './commons_pictures/'
   - Format as:
     <div style="float: right; margin: 0 0 20px 20px; max-width: 40%;">
       <img src="[path]" alt="[title]" style="width: 100%; height: auto;"/>
       <p style="font-size: 0.9em; text-align: center;"><em>[concise_caption]</em></p>
     </div>
   - Place it near the text it relates to based on explanation_of_relevance
   - Create a brief, informative caption (1-2 lines)

Return the section with original text intact and images properly inserted."""

    client = OpenAI(api_key="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")
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "You are an AI that carefully adds images to article sections while preserving the exact original text."},
            {"role": "user", "content": prompt}
        ],
        response_format=FormattedSection,
    )
    
    return completion.choices[0].message.parsed.formatted_content

def get_sections_to_format(selected_images: Dict) -> set:
    """Get set of section titles that need image formatting."""
    return set(img["section"] for img in selected_images.get("images", []))

def integrate_images():
    """Integrate selected images into the article while preserving original content."""
    print("\n📝 Integrating images into article...")
    
    # Read all required files
    article_text = read_article()
    outline = read_outline()
    selected_images = read_selected_images()
    
    # Identify sections that need formatting
    sections_to_format = get_sections_to_format(selected_images)
    print(f"\n🔍 Found {len(sections_to_format)} sections that need image formatting")
    
    # Initialize the final article content
    final_article = article_text
    
    # Process each section that needs formatting
    for section_title in sections_to_format:
        print(f"\n🖼️ Processing section: {section_title}")
        
        # Find section in original text
        pattern = rf"(#+\s*{re.escape(section_title)}\n.*?)(?=#+\s|$)"
        match = re.search(pattern, article_text, re.DOTALL)
        
        if match:
            # Get original section content
            original_section = match.group(0).strip()
            
            # Get images for this section
            section_images = [img for img in selected_images["images"] 
                            if img["section"] == section_title]
            
            # Format section with images
            formatted_section = format_section_with_images(section_title, original_section, section_images)
            
            # Replace original section with formatted section
            final_article = final_article.replace(original_section, formatted_section)
            print(f"✅ Added images to section: {section_title}")
        else:
            print(f"⚠️ Could not find section: {section_title} in article")
    
    # Save the final article
    with open("article_with_images.md", 'w', encoding='utf-8') as f:
        f.write(final_article)
    
    print("\n✅ Formatted article saved to article_with_images.md")

if __name__ == "__main__":
    print("🎯 Starting Image Integration Process")
    try:
        integrate_images()
        print("\n✨ Article integration completed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")