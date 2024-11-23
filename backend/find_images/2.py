import requests
import json
from datetime import datetime
import os
import time
import shutil  # Add this import at the top of the file
import sys


def sanitize_filename(filename):
    """Sanitize filename to be safe for all operating systems"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:200]  # Limit length to avoid path too long errors

def search_images(query, api_key, cx, num_images=10):
    """
    Search for images using Google Custom Search API without downloading
    """
    base_url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        'q': query + " -site:chegg.com  -site:alamy.com -site:slideshare.com",  # Exclude Chegg from search results
        'key': api_key,
        'cx': cx,
        'searchType': 'image',
        'num': num_images
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        search_results = response.json()
        
        images = []
        for item in search_results.get('items', []):
            image_data = {
                'title': item.get('title'),
                'link': item.get('link'),
                'thumbnail': item.get('image', {}).get('thumbnailLink'),
                'context_link': item.get('image', {}).get('contextLink'),
                'width': item.get('image', {}).get('width'),
                'height': item.get('image', {}).get('height'),
                'size': item.get('image', {}).get('byteSize'),
                'format': item.get('fileFormat'),
                'snippet': item.get('snippet'),
                'saved_filename': f"image_{len(images):02d}.jpg"  # Simulated filename
            }
            images.append(image_data)
            
        return images[:5]  # Return only first 5 results
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return []

def process_search_results(suggestion, api_key, cx, base_dir="image_searches"):
    """Process search results for a single suggestion without downloading images"""
    query = suggestion['search_query']
    index = suggestion['index']
    
    # Create folder for this search query
    folder_name = sanitize_filename(f"{index:02d}_{query}")
    folder_path = os.path.join(base_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    # Search for images
    results = search_images(query, api_key, cx)
    
    # Save metadata
    metadata = {
        'query': query,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'original_quote': suggestion['quote'],
        'section_title': suggestion['section_title'],
        'reason': suggestion['reason'],
        'description': suggestion['image_description'],
        'images': results
    }
    
    metadata_path = os.path.join(folder_path, 'metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return len(results)

def main():
    # Configuration
    API_KEY = "AIzaSyDTUZdD1RhA9oey878fzA5o3REMnymR9hk"
    CX = "33f4586468b0c41e6"
    BASE_DIR = "image_searches"
    
    # In main(), add this before os.makedirs():
    if os.path.exists(BASE_DIR):
        shutil.rmtree(BASE_DIR)
        # Create base directory
        os.makedirs(BASE_DIR, exist_ok=True)
    
    # Read the analysis results
    try:
        with open('analysis_result.json', 'r', encoding='utf-8') as f:
            analysis = json.load(f)
    except FileNotFoundError:
        print("Error: analysis_result.json not found!")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON in analysis_result.json!")
        return
    
    # Process each suggestion
    total_suggestions = len(analysis['suggestions'])
    print(f"Processing {total_suggestions} search queries...")
    
    for suggestion in analysis['suggestions']:
        #print(f"\nProcessing search query {suggestion['index']}/{total_suggestions}: {suggestion['search_query']}")
        num_processed = process_search_results(suggestion, API_KEY, CX, BASE_DIR)
        #print(f"Successfully processed {num_processed} image results")
        time.sleep(0.1)  # Small delay between searches
    
    print("\nAll searches completed!")

if __name__ == "__main__":
    main()