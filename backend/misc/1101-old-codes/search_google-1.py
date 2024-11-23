#Search_google-1.py
import requests
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
import json
from datetime import datetime
import os
# Import the webpage extraction function directly
from extract_webpage import save_content_html

class URLAnalysis(BaseModel):
    relevant_urls: List[str] = Field(description="List of URLs that are most relevant to the topic")
    reasons: List[str] = Field(description="Reasons why each URL is relevant")
    file_names: List[str] = Field(description="Suggested file names for each URL's content")

def analyze_search_results(search_results: str, topic: str, api_key: str) -> URLAnalysis:
    """
    Analyze search results using GPT to find most relevant URLs and suggest file names
    """
    client = OpenAI(api_key=api_key)
    
    system_prompt = f"""
    You are an expert at analyzing search results to find the most relevant URLs for a given topic.
    Analyze the search results and return only URLs that provide comprehensive, reliable information about: {topic}
    Focus on educational, scientific, and authoritative sources.
    Limit to maximum 3-5 most relevant URLs.
    For each URL, suggest a descriptive filename (without .html extension) that:
    1. Reflects the content
    2. Uses only lowercase letters, numbers, and underscores
    3. Is unique among all suggested names
    4. Is between 20-50 characters long
    """
    
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=URLAnalysis,
            messages=[
                {"role": "user", "content": system_prompt},
                {"role": "user", "content": f"Search results:\n{search_results}\n\nPlease analyze and return the most relevant URLs with suggested file names in JSON format."}
            ]
        )
        
        result = json.loads(completion.choices[0].message.content)
        return URLAnalysis(**result)
        
    except Exception as e:
        print(f"Error in GPT analysis: {e}")
        return URLAnalysis(relevant_urls=[], reasons=[], file_names=[])

def google_search_and_analyze(query: str, openai_api_key: str) -> List[dict]:
    """
    Perform Google search, analyze results with GPT, and extract webpage content
    Returns list of dictionaries containing URL and saved filename
    """
    API_KEY = "AIzaSyDTUZdD1RhA9oey878fzA5o3REMnymR9hk"
    CX = "33f4586468b0c41e6"
    
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': API_KEY,
        'cx': CX,
        'q': query,
        'num': 10
    }
    
    saved_files = []
    
    try:
        # Create source_html directory if it doesn't exist
        os.makedirs('source_html', exist_ok=True)
        
        # Perform Google search
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        search_results = response.json()
        
        # Format results for GPT analysis
        formatted_results = []
        if 'items' in search_results:
            for item in search_results['items']:
                formatted_results.append({
                    'title': item.get('title', 'N/A'),
                    'url': item.get('link', 'N/A'),
                    'description': item.get('snippet', 'N/A')
                })
        
        # Save raw Google search results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_results_filename = f"search_results_{timestamp}.txt"
        
        with open(raw_results_filename, 'w', encoding='utf-8') as f:
            f.write(f"Search Query: {query}\n")
            f.write(f"Search Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("Raw Google Search Results:\n")
            f.write("-" * 100 + "\n")
            f.write(json.dumps(formatted_results, indent=2))
            f.write("\n" + "-" * 100 + "\n\n")
        
        # Analyze with GPT
        analysis = analyze_search_results(
            json.dumps(formatted_results, indent=2),
            query,
            openai_api_key
        )
        
        # Append GPT analysis to the same file
        with open(raw_results_filename, 'a', encoding='utf-8') as f:
            f.write("GPT Analysis Results:\n")
            f.write("-" * 100 + "\n")
            for url, reason, filename in zip(analysis.relevant_urls, analysis.reasons, analysis.file_names):
                f.write(f"URL: {url}\n")
                f.write(f"Reason for relevance: {reason}\n")
                f.write(f"Suggested filename: {filename}.html\n")
                f.write("-" * 100 + "\n")
        
        print(f"\nSearch results and analysis saved to {raw_results_filename}")
        
        # Extract and save content from each relevant URL
        print("\nExtracting content from relevant URLs...")
        for url, filename in zip(analysis.relevant_urls, analysis.file_names):
            try:
                full_path = os.path.join('source_html', f"{filename}.html")
                saved_filename = save_content_html(url, full_path)
                saved_files.append({
                    'url': url,
                    'filename': saved_filename
                })
                print(f"Content from {url} saved to {saved_filename}")
            except Exception as e:
                print(f"Error extracting content from {url}: {e}")
        
        return saved_files
        
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    OPENAI_API_KEY = "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"
    
    try:
        # Read search query from topic.txt
        with open('topic.txt', 'r', encoding='utf-8') as f:
            search_query = f.read().strip()
        
        if not search_query:
            raise ValueError("topic.txt is empty")
            
        print(f"Search query loaded from topic.txt: {search_query}")
        saved_files = google_search_and_analyze(search_query, OPENAI_API_KEY)
        
        if saved_files:
            print("\nSummary of saved files:")
            for file_info in saved_files:
                print(f"URL: {file_info['url']}")
                print(f"Saved as: {file_info['filename']}")
                print("-" * 50)
    except FileNotFoundError:
        print("Error: topic.txt file not found. Please create a topic.txt file with your search query.")
    except Exception as e:
        print(f"Error reading topic.txt: {e}")