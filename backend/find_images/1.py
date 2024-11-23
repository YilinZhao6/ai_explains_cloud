from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
import re
import json


class ImageSuggestion(BaseModel):
    index: int = Field(
        description="The sequential number of this image suggestion in the document"
    )
    quote: str = Field(
        description="The specific quote from the text that needs visual illustration"
    )
    section_title: str = Field(
        description="The title of the section where the quote comes from"
    )
    reason: str = Field(
        description="Explanation of why this passage needs an image and how it would enhance understanding"
    )
    image_description: str = Field(
        description="Detailed description of what the ideal image should contain"
    )
    search_query: str = Field(
        description="Precise search query to find an appropriate academic/textbook-style image"
    )

class DocumentAnalysis(BaseModel):
    suggestions: List[ImageSuggestion]
    total_suggestions: int

def extract_section_titles(markdown_content: str) -> List[str]:
    """
    Extract section titles that start with '##' in the markdown content.
    
    Args:
        markdown_content (str): The content of the markdown file.
        
    Returns:
        List[str]: A list of section titles.
    """
    return re.findall(r'^##\s+(.+)$', markdown_content, re.MULTILINE)

def analyze_markdown(markdown_content: str, section_titles: List[str]) -> DocumentAnalysis:
    client = OpenAI(api_key="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")
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": f"""You are an expert textbook editor. Analyze the provided text and identify passages that need images.
                Consider:
                1. The main concept needing visualization (the main concept being explained in this passage)
                2. Some images related to the examples in application part

                Note:
                1. Remember, the search queries you returned will be later used to search for images on the Internet, which don't have everything you want.
                Note: You MUST NOT look for a specific arrangement of diagram! (e.g., A bad search query is "two boxes with yellow red balls illustration." You MUST not look for graphs like this!)
                2. When quoting, please make sure to quote the complex concept itself fully.
                3. Each image you find should not be related to each other.
                4. The image you search should visualize the concept the article is introducing. Normally one image per section would be fine.
                5. Do not search for images that are like logical diagrams! These queries will lead to poor results.
                6. The image must only focus on one subject! Comparison graphs, or analogical graphs are not permitted.
                7. Return 5 images at most for this article.
                8. IMPORTANT: the section_title MUST be one of the following titles:
                {section_titles}
                You will be severely punished for giving anything other than this title.
                """
            },
            {"role": "user", "content": markdown_content}
        ],
        response_format=DocumentAnalysis,
    )
    
    return completion.choices[0].message.parsed

def save_analysis_to_json(analysis: DocumentAnalysis, output_file: str = "analysis_result.json"):
    """
    Save the DocumentAnalysis result to a JSON file.
    
    Args:
        analysis (DocumentAnalysis): The analysis result to save
        output_file (str): The path to save the JSON file (default: 'analysis_result.json')
    """
    # Convert the Pydantic model to a dictionary
    analysis_dict = analysis.dict()  # Changed from model_dump() to dict()
    
    # Save to JSON file with proper formatting
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_dict, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Read markdown file
    with open("article.md", "r", encoding="utf-8") as f:
        markdown_content = f.read()
    
    # Extract section titles
    section_titles = extract_section_titles(markdown_content)
    
    # Analyze the content
    analysis = analyze_markdown(markdown_content, section_titles)
    
    # Save results to JSON file
    save_analysis_to_json(analysis)
    
    print(f"Analysis results have been saved to analysis_result.json")
    
    # Print results in a formatted way
    """print(f"\nFound {analysis.total_suggestions} passages requiring images:\n")
    for suggestion in analysis.suggestions:
        print(f"Image {suggestion.index}:")
        print(f"Quote: {suggestion.quote}")
        print(f"Section Title: {suggestion.section_title}")
        print(f"Reason: {suggestion.reason}")
        print(f"Ideal Image: {suggestion.image_description}")
        print(f"Search Query: {suggestion.search_query}\n")"""
