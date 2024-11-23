import requests
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
import json
import sys
from datetime import datetime
import os

class URLAnalysis(BaseModel):
    relevant_urls: List[str] = Field(description="List of URLs that are most relevant to the topic")
    reasons: List[str] = Field(description="Reasons why each URL is relevant")

def analyze_search_results(search_results: str, topic: str, api_key: str) -> URLAnalysis:
    """
    Analyze search results using GPT to find most relevant URLs
    """
    client = OpenAI(api_key=api_key)
    
    system_prompt = f"""
    You are an expert at analyzing search results to find the most relevant URLs for a given topic.
    Analyze the search results and return only URLs that provide comprehensive, reliable information about: {topic}
    Focus on educational, scientific, and authoritative sources.
    Limit to maximum 3-5 most relevant URLs.
    """
    
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=URLAnalysis,
            messages=[
                {"role": "user", "content": system_prompt},
                {"role": "user", "content": f"Search results:\n{search_results}\n\nPlease analyze and return the most relevant URLs in JSON format."}
            ]
        )
        
        result = json.loads(completion.choices[0].message.content)
        return URLAnalysis(**result)
        
    except Exception as e:
        print(f"Error in GPT analysis: {e}")
        return URLAnalysis(relevant_urls=[], reasons=[])

def google_search_and_analyze(query: str, openai_api_key: str) -> None:
    """
    Perform Google search and analyze results with GPT
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
    
    try:
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
        
        # Analyze with GPT
        analysis = analyze_search_results(
            json.dumps(formatted_results, indent=2),
            query,
            openai_api_key
        )
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relevant_urls_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Search Query: {query}\n")
            f.write(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for url, reason in zip(analysis.relevant_urls, analysis.reasons):
                f.write(f"URL: {url}\n")
                f.write(f"Reason for relevance: {reason}\n")
                f.write("-" * 100 + "\n")
        
        print(f"\nAnalysis saved to {filename}")
        return analysis.relevant_urls
        
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    OPENAI_API_KEY = "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"
    
    search_query = input("Enter your search query: ")
    relevant_urls = google_search_and_analyze(search_query, OPENAI_API_KEY)
    
    if relevant_urls:
        print("\nCalling webpage extractor for relevant URLs...")
        urls_arg = " ".join(relevant_urls)
        os.system(f"python extract_webpage.py {urls_arg}")