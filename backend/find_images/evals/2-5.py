import requests
import json
from datetime import datetime
import os
import time
from pathlib import Path
import shutil

def sanitize_filename(filename):
    """Sanitize filename to be safe for all operating systems"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:200]  # Limit length to avoid path too long errors

def search_images(query, api_key, cx, num_images=5):
    """
    Search for images using Google Custom Search API
    """
    base_url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        'q': query,
        'key': api_key,
        'cx': cx,
        'searchType': 'image',
        'num': min(num_images, 5)  # API limits to 10 per request
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
                'snippet': item.get('snippet')
            }
            images.append(image_data)
            
        return images
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return []

def download_image(url, folder_path, index):
    """Download an image and save it to the specified folder"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file extension from Content-Type if available
        content_type = response.headers.get('content-type', '')
        ext = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp'
        }.get(content_type, '.jpg')
        
        filename = f"image_{index:02d}{ext}"
        file_path = os.path.join(folder_path, filename)
        
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
            
        return filename
    except Exception as e:
        print(f"Error downloading image {url}: {e}")
        return None

def process_search_results(suggestion, api_key, cx, base_dir="image_searches"):
    """Process search results for a single suggestion"""
    query = suggestion['search_query']
    index = suggestion['index']
    
    # Create folder for this search query
    folder_name = sanitize_filename(f"{index:02d}_{query}")
    folder_path = os.path.join(base_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    # Search for images
    results = search_images(query, api_key, cx)
    
    # Download images and update metadata
    downloaded_images = []
    for i, result in enumerate(results):
        filename = download_image(result['link'], folder_path, i)
        if filename:
            result['saved_filename'] = filename
            downloaded_images.append(result)
        time.sleep(0.5)  # Add delay between downloads
    
    # Save metadata
    metadata = {
        'query': query,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'original_quote': suggestion['quote'],
        'reason': suggestion['reason'],
        'description': suggestion['image_description'],
        'images': downloaded_images
    }
    
    metadata_path = os.path.join(folder_path, 'metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return len(downloaded_images)

def main():
    # Configuration
    API_KEY = "AIzaSyDTUZdD1RhA9oey878fzA5o3REMnymR9hk"
    CX = "33f4586468b0c41e6"
    BASE_DIR = "image_searches"
    
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
        print(f"\nProcessing search query {suggestion['index']}/{total_suggestions}: {suggestion['search_query']}")
        num_downloaded = process_search_results(suggestion, API_KEY, CX, BASE_DIR)
        print(f"Downloaded {num_downloaded} images")
        time.sleep(2)  # Add delay between searches
    
    print("\nAll searches completed!")

if __name__ == "__main__":
    main()