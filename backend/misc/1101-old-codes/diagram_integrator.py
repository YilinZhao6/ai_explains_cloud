from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json
import sys
import time
from pathlib import Path
from openai import OpenAI
import re

sys.stdout.reconfigure(encoding='utf-8')

class ImageInfo(BaseModel):
    filename: str
    title: str
    description: str
    resolution: str
    local_path: str
    section: str = Field(description="Article section this image belongs to")
    relevance_score: float = Field(description="Score indicating relevance to the section (0-1)")

class SelectedImages(BaseModel):
    images: List[ImageInfo]

class FormattedSection(BaseModel):
    section_title: str
    formatted_content: str = Field(description="Markdown formatted content with integrated images")

def read_article(file_path: str = "article.md") -> str:
    """Read the article content."""
    print("\n📄 Reading article content...")
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_commons_folders() -> List[Path]:
    """Get all subfolders in commons_pictures directory."""
    commons_dir = Path("commons_pictures")
    return [d for d in commons_dir.iterdir() if d.is_dir()]

def analyze_and_select_images() -> Dict:
    """Analyze images and select the most relevant ones for each section."""
    print("\n🔍 Analyzing downloaded images...")
    
    article_text = read_article()
    
    # Read all metadata files
    all_images = []
    for folder in get_commons_folders():
        metadata_file = folder / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                for img in metadata.get("images", []):
                    img["search_query"] = metadata.get("search_query", "")
                    all_images.append(img)

    print(f"Found {len(all_images)} total images")

    # Create prompt for image selection
    prompt = f"""Analyze these images and the article content to select the most relevant images for each section.

Article Content:
{article_text}

Available Images:
{json.dumps(all_images, indent=2)}

Select the most appropriate images considering:
1. Relevance to section content
2. Image quality and resolution
3. Clear and educational value
4. Caption informativeness

Return a list of selected images with their metadata and assigned sections."""

    client = OpenAI(api_key="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")
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "You are an AI that selects and organizes images for educational articles."},
            {"role": "user", "content": prompt}
        ],
        response_format=SelectedImages,
    )
    
    selected_images = completion.choices[0].message.parsed.dict()
    
    # Save selected images to JSON
    with open("selected_images.json", 'w', encoding='utf-8') as f:
        json.dump(selected_images, f, indent=2, ensure_ascii=False)
    
    print("✅ Selected images saved to selected_images.json")
    return selected_images

def format_section_with_images(section_title: str, section_content: str, section_images: List[Dict]) -> str:
    """Format a single section with its images."""
    prompt = f"""Format this article section with the provided images:

Section Title: {section_title}

Content:
{section_content}

Available Images for this section:
{json.dumps(section_images, indent=2)}

Guidelines:
1. Place images on the right side of the text
2. Add Wikipedia-style captions
3. Use appropriate image sizing based on resolution
4. Format in Markdown
5. Maintain good text-image balance

Return the formatted Markdown content with integrated images."""

    client = OpenAI(api_key="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")
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "You are an AI that formats educational content with images."},
            {"role": "user", "content": prompt}
        ],
        response_format=FormattedSection,
    )
    
    return completion.choices[0].message.parsed.formatted_content

def integrate_images_into_article(selected_images: Dict):
    """Integrate selected images into the article."""
    print("\n📝 Integrating images into article...")
    
    article_text = read_article()
    
    # Split article into sections (assuming sections are marked with markdown headers)
    sections = re.split(r'(?=#+\s)', article_text)
    sections = [s.strip() for s in sections if s.strip()]
    
    formatted_sections = []
    for section in sections:
        # Extract section title from the first line
        section_title = section.split('\n')[0].strip('#').strip()
        section_content = '\n'.join(section.split('\n')[1:]).strip()
        
        # Get images for this section
        section_images = [img for img in selected_images["images"] 
                        if img["section"].lower() == section_title.lower()]
        
        # Format section with images
        formatted_section = format_section_with_images(section_title, section_content, section_images)
        formatted_sections.append(formatted_section)
    
    # Combine formatted sections
    final_article = '\n\n'.join(formatted_sections)
    
    # Save the formatted article
    with open("article_with_images.md", 'w', encoding='utf-8') as f:
        f.write(final_article)
    
    print("✅ Formatted article saved to article_with_images.md")

def main():
    try:
        print("🎯 Starting Image Integration Process")
        
        # Step 1: Analyze and select images
        selected_images = analyze_and_select_images()
        
        # Step 2: Sleep for 10 seconds
        print("\n⏳ Waiting for 10 seconds...")
        time.sleep(10)
        
        # Step 3: Integrate images into article
        integrate_images_into_article(selected_images)
        
        print("\n✨ Article integration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()