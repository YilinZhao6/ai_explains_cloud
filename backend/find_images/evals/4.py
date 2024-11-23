import json
import re
import os
from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel
import sys


class TextResponse(BaseModel):
    text: str

def split_markdown_sections(file_path: Path) -> dict:
    """Split markdown file into sections based on ## headings."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    sections = re.split(r'(## .+)', content)
    section_map = {}

    for i in range(1, len(sections), 2):
        title = sections[i].strip()
        body = sections[i + 1].strip()
        section_map[title] = body

    return section_map

def update_section_with_image(client: OpenAI, section_title: str, section_content: str, image_data: dict, original_quote: str) -> str:
    """Send request to OpenAI to generate updated section with image integrated at the right position."""
    # Prepare prompt content with section content, image details, and quote
    content = [
        {"type": "text", "text": f"Section: {section_title}\n\n{section_content}"},
        {"type": "text", "text": (
            "Please integrate the following image next to the relevant quote on the right side, using HTML. "
            "IMPORTANT: The section may already contain previously added images. You MUST preserve ALL existing "
            "images and texts that are already in the section - do not modify or remove any existing image figures or texts!. "
            "Do not modify any header formatting. If a header starts with ###, it MUST remain ###. If it starts with ##, it MUST remain ##. Preserve the EXACT number of # symbols in ALL headers!\n"
            "Only add this new image next to its corresponding quote while keeping all other images in their current positions.\n\n"
            "CRITICAL HTML STRUCTURE REQUIREMENTS:\n"
            "1. Each paragraph should be wrapped in its own <p> tag\n"
            "2. Images should be placed in a Wikipedia-style box with this exact structure:\n"
            "<figure style=\"float: right; clear: right; margin: 0 0 20px 20px; max-width: 30%; background-color: #f8f9fa; border: 1px solid #a2a9b1; padding: 8px; box-sizing: border-box;\">\n"
            "    <div style=\"background-color: #f8f9fa; text-align: center; padding: 5px;\">\n"
            "        <img src=\"{image_src}\" alt=\"{alt_text}\" style=\"width: 100%; height: auto; display: block; margin: 0 auto;\"/>\n"
            "    </div>\n"
            "    <figcaption style=\"border-top: 1px solid #a2a9b1; margin-top: 8px; padding-top: 8px;\">\n"
            "        <div style=\"font-size: 0.9em; text-align: center;\">\n"
            "            <em>{caption}</em>\n"
            "        </div>\n"
            "        <div style=\"font-size: 0.8em; text-align: center; margin-top: 4px;\">\n"
            "            <a href=\"{source}\" style=\"display: inline-block; padding: 2px 8px; background-color: #f8f9fa; border: 1px solid #a2a9b1; border-radius: 3px; color: #202122; text-decoration: none; cursor: pointer;\" target=\"_blank\">Source</a>\n"
            "        </div>\n"
            "    </figcaption>\n"
            "</figure>\n\n"
            "3. Use the <figure> tag with Wikipedia-style formatting\n"
            "4. Always include 'clear: right' in the figure style to prevent floating conflicts\n"
            "5. Do not wrap the entire section content in an unnecessary outer div\n"
            "6. The source should be a clickable button that opens in a new tab\n"

                            )},
        {"type": "text", "text": (
            f"Image data:\n"
            f"Filename: {image_data['saved_filename']},\n"
            f"URL: {image_data['link']},\n"
            f"Alt text: {image_data['explanation']},\n"
            f"Caption: {image_data['caption']}\n"
            f"Original Quote: {original_quote}\n\n"
            f"Remember: DO NOT remove or modify any existing image figures in the section! "
            f"Use the exact HTML structure specified above for the new image!"
        )}
    ]

    # Send the request to OpenAI
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": content}],
        response_format=TextResponse,
        temperature=0,
    )
    
    # Return the generated text to update the section
    return response.choices[0].message.parsed.text

def write_updated_article(section_map: dict, output_path: Path):
    """Write updated sections to a new markdown file."""
    with open(output_path, 'w', encoding='utf-8') as file:
        for title, content in section_map.items():
            file.write(f"{title}\n{content}\n\n")

def get_latest_section_content(output_path: Path, section_title: str) -> str:
    """Get the most recent content for a specific section from the output file."""
    section_map = split_markdown_sections(output_path)
    return section_map.get(section_title, "")

def process_image_integration(client: OpenAI, section_map: dict, image_folder: Path, output_path: Path):
    """Process images sequentially, writing each update before processing the next image."""
    
    # First, write the initial section map to the output file
    write_updated_article(section_map, output_path)
    
    # Get all image JSONs and sort them (to ensure consistent processing order)
    json_paths = sorted(image_folder.glob("*/selected_image.json"))
    
    for json_path in json_paths:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        section_title = f"## {data['section_title']}"
        
        # Get the latest content for this section from the output file
        latest_section_content = get_latest_section_content(output_path, section_title)
        
        if latest_section_content:
            #print(f"Integrating image for section: {section_title}")

            # Generate the updated section content with the image integration
            # using the latest content from the file
            updated_content = update_section_with_image(
                client,
                section_title,
                latest_section_content,  # Use the latest content instead of original
                data['selected_image'],
                data['original_quote']
            )

            # Read the current state of the entire article
            current_section_map = split_markdown_sections(output_path)
            
            # Update the specific section with new content
            current_section_map[section_title] = updated_content
            
            # Write the updated content back to file immediately
            write_updated_article(current_section_map, output_path)
        else:
            print(f"Warning: Section title '{data['section_title']}' not found in article.md")

def main():
    # Configuration
    client = OpenAI(api_key="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")
    article_path = Path("article.md")
    image_folder = Path("image_searches")
    output_path = Path("updated_article.md")

    # Split the article into sections based on ## headings
    initial_section_map = split_markdown_sections(article_path)

    # Process images sequentially, writing each update to file
    process_image_integration(client, initial_section_map, image_folder, output_path)

    print(f"Updated article has been saved to {output_path}")

if __name__ == "__main__":
    main()