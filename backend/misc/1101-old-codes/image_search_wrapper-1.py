from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import json
import sys
from pathlib import Path
from openai import OpenAI
import time

sys.stdout.reconfigure(encoding='utf-8')

class ImageInfo(BaseModel):
    filename: str
    title: str
    description: str
    resolution: str
    local_path: str
    section: str = Field(description="Section title from the outline that this image belongs to")
    relevance_score: float = Field(description="Score indicating relevance to the section (0-1)")
    explanation_of_relevance: str = Field(description="Specific explanation of how this image relates to the section content")

class SelectedImages(BaseModel):
    images: List[ImageInfo]

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

def get_section_titles(outline: dict) -> List[str]:
    """Extract section titles from outline."""
    return [section["section_title"] for section in outline.get("sections", [])]

def get_commons_folders() -> List[Path]:
    """Get all subfolders in commons_pictures directory."""
    commons_dir = Path("commons_pictures")
    return [d for d in commons_dir.iterdir() if d.is_dir()]

def select_images():
    """Analyze images and select the most relevant ones for each section."""
    print("\n🔍 Analyzing downloaded images...")
    
    article_text = read_article()
    outline = read_outline()
    section_titles = get_section_titles(outline)
    
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

    prompt = f"""Analyze these images and select the most relevant ones for each section of the article.

Article Content:
{article_text}

Article Outline Sections:
{json.dumps(section_titles, indent=2)}

Available Images:
{json.dumps(all_images, indent=2)}

Selection Guidelines:
1. Select maximum 2-3 images per section to maintain readability
2. Images MUST be assigned to sections using EXACT section titles from the outline
3. For each image, provide a detailed explanation of how it relates to specific content within that section
4. Prioritize images that:
   - Best illustrate key concepts
   - Have high clarity and educational value
   - Have clear, informative descriptions
5. Ensure even distribution across sections
6. Avoid redundant or very similar images
7. Consider image resolution and quality

For each selected image, you must include:
- The exact section title from the outline
- A specific explanation of how the image relates to the section's content
- A relevance score (0-1) based on how well it illustrates the concept

Return a list of selected images with their complete metadata and assignments."""

    client = OpenAI(api_key="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")
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI that selects and assigns images to specific sections of educational articles, providing detailed explanations of their relevance."},
            {"role": "user", "content": prompt}
        ],
        response_format=SelectedImages,
    )
    
    selected_images = completion.choices[0].message.parsed.dict()
    
    # Save selected images to JSON
    with open("selected_images.json", 'w', encoding='utf-8') as f:
        json.dump(selected_images, f, indent=2, ensure_ascii=False)
    
    print("✅ Selected images saved to selected_images.json")

if __name__ == "__main__":
    print("🎯 Starting Image Selection Process")
    try:
        select_images()
        print("\n✨ Image selection completed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")