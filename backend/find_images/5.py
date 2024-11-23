import re
from pathlib import Path

def split_and_save_markdown_sections(file_path: Path) -> None:
    """
    Split markdown file into separate files based on ## headings only (level 2).
    Each file contains all content (including ### subsections) until the next ## heading.
    
    Parameters:
    file_path (Path): Path to the markdown file to split
    """
    # Read the markdown file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Find all level 2 headings and their positions
    level2_matches = list(re.finditer(r'^## .+$', content, re.MULTILINE))
    
    # Create sections directory if it doesn't exist
    sections_dir = Path('sections')
    sections_dir.mkdir(exist_ok=True)
    
    # Process each section
    for i, match in enumerate(level2_matches):
        # Get the start position of this section
        start_pos = match.start()
        
        # Get the end position (either the start of next section or end of file)
        if i < len(level2_matches) - 1:
            end_pos = level2_matches[i + 1].start()
        else:
            end_pos = len(content)
        
        # Extract the section content (including the heading)
        section_content = content[start_pos:end_pos].strip()
        
        # Get the section title (without the ## prefix)
        title = match.group().replace('## ', '').strip()
        
        # Create filename
        filename = title.lower()
        filename = re.sub(r'[\s\-]+', '_', filename)
        filename = re.sub(r'[^\w\s\-]', '', filename)
        filename = f"{filename}.md"
        
        # Create the full file path
        file_path = sections_dir / filename
        
        # Save the section with all its content
        with open(file_path, 'w', encoding='utf-8') as section_file:
            section_file.write(section_content + '\n')
            
    print(f"Sections have been saved in the '{sections_dir}' directory")

if __name__ == "__main__":
    # Usage example
    markdown_file = Path("article.md")
    split_and_save_markdown_sections(markdown_file)