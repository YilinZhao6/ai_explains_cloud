"""
Image Retrieval Script from Wikimedia Commons
-------------------------------------------

Usage:
    python image_retrieval_command_args.py [-h] keyword_limits [keyword_limits ...]

Arguments:
    keyword_limits   Keywords and their limits in the format "keyword:limit" or just "keyword" (uses default limit)
                    If no limit is specified for a keyword, default limit (5) is used.
                    Wrap keywords containing spaces in quotes.

                    Examples: 
                    - "moment of inertia:3"
                    - "jet planes:5" 
                    - trains:8
                    - "quantum physics"  (will use default limit of 5)

Optional Arguments:
    -h, --help      Show this help message and exit
    -d, --default LIMIT
                    Set default number of images (default: 5) for keywords without specified limits

Examples:
    1. Download with specific limits for each keyword:
       python image_retrieval_command_args.py "moment of inertia:3" "jet planes:5" "trains:8"

    2. Mix specific limits and default limit:
       python image_retrieval_command_args.py "moment of inertia:3" "quantum physics" "trains:8"
       (quantum physics will use default limit of 5)

    3. Change default limit to 10 for unspecified keywords:
       python image_retrieval_command_args.py -d 10 "moment of inertia:3" "quantum physics" "trains:8"
       (quantum physics will use default limit of 10)

    4. Single keyword with specific limit:
       python image_retrieval_command_args.py "moment of inertia:3"

Output:
    Creates a directory structure under 'commons_pictures/':
    commons_pictures/
    ├── moment_of_inertia/
    │   ├── image1.jpg
    │   ├── image2.png
    │   └── metadata.json
    ├── jet_planes/
    │   ├── image1.svg
    │   ├── image2.gif
    │   └── metadata.json
    └── trains/
        ├── image1.jpg
        ├── image2.png
        └── metadata.json
"""

import requests
import os
import json
import urllib.parse
from typing import List, Dict, Tuple
import time
import argparse
import sys
from pathlib import Path

HEADERS = {
    'User-Agent': 'WikimediaImageDownloader/1.0 (https://github.com/yourusername; your@email.com) Python/3.x'
}

def parse_keyword_limit(keyword_limit: str, default_limit: int) -> Tuple[str, int]:
    """Parse keyword:limit string into separate keyword and limit."""
    if ':' in keyword_limit:
        keyword, limit = keyword_limit.rsplit(':', 1)
        try:
            return keyword.strip(), int(limit)
        except ValueError:
            print(f"Warning: Invalid limit format for '{keyword_limit}', using default limit {default_limit}")
            return keyword_limit, default_limit
    return keyword_limit, default_limit

def create_safe_directory_name(query: str) -> str:
    """Create a safe directory name from the search query."""
    return "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in query.lower())

def search_wikimedia_commons(query: str, limit: int = 5) -> List[Dict]:
    """
    Search Wikimedia Commons for images using the given query.
    Returns metadata for the top matches.
    """
    api_url = "https://commons.wikimedia.org/w/api.php"
    
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"file: {query}",
        "gsrlimit": limit,
        "prop": "imageinfo|info|categories",
        "iiprop": "url|size|extmetadata",
        "iiurlwidth": 1920,
        "inprop": "url",
        "iimetadataversion": "latest",
    }
    
    try:
        response = requests.get(api_url, params=params, headers=HEADERS)
        data = response.json()
        
        if "query" not in data or "pages" not in data["query"]:
            print(f"No results found for query: {query}")
            return []
        
        results = []
        for page in data["query"]["pages"].values():
            if "imageinfo" not in page:
                continue
                
            info = page["imageinfo"][0]
            ext_metadata = info.get("extmetadata", {})
            
            description = (
                ext_metadata.get("ImageDescription", {}).get("value", "")
                or ext_metadata.get("Description", {}).get("value", "")
            )
            
            description = description.replace("<br>", "\n").replace("<br />", "\n")
            description = ' '.join(description.split())
            
            if not description.strip():
                continue
                
            result = {
                "title": page.get("title", "").replace("File:", ""),
                "description": description,
                "url": info.get("url", ""),
                "thumb_url": info.get("thumburl", ""),
                "width": info.get("width", 0),
                "height": info.get("height", 0),
                "size": info.get("size", 0),
                "mime": info.get("mime", ""),
                "commons_url": page.get("canonicalurl", "")
            }
            results.append(result)
            
        return results
    
    except Exception as e:
        print(f"Error searching Wikimedia Commons for {query}: {str(e)}")
        return []

def download_images(results: List[Dict], search_query: str) -> List[Dict]:
    """Download images and save their metadata. Returns list of metadata dictionaries."""
    base_dir = Path("commons_pictures")
    base_dir.mkdir(exist_ok=True)
    
    output_dir = base_dir / create_safe_directory_name(search_query)
    output_dir.mkdir(exist_ok=True)
    
    all_metadata = []
    
    for idx, result in enumerate(results, 1):
        base_filename = result["title"]
        safe_filename = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in base_filename)
        
        ext = result["mime"].split("/")[-1] if result["mime"] else result["url"].split(".")[-1]
        image_filename = f"{safe_filename}.{ext}"
        
        try:
            print(f"\nDownloading {idx}/{len(results)}: {result['title']}")
            
            response = requests.get(result["url"], headers=HEADERS, stream=True)
            
            if response.status_code == 200:
                image_path = output_dir / image_filename
                with open(image_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                metadata = {
                    "filename": image_filename,
                    "title": result["title"],
                    "description": result["description"],
                    "resolution": f"{result['width']}x{result['height']}",
                    "size_bytes": result["size"],
                    "mime_type": result["mime"],
                    "commons_url": result["commons_url"],
                    "local_path": str(image_path.absolute())
                }
                
                all_metadata.append(metadata)
                print(f"Successfully downloaded: {image_filename}")
                print(f"Description: {result['description'][:100]}...")
                
            else:
                print(f"Failed to download image: HTTP {response.status_code}")
                print("Skipping this image.")
                
        except Exception as e:
            print(f"Error downloading {result['title']}: {str(e)}")
        
        time.sleep(1)
    
    if all_metadata:
        metadata_path = output_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8', errors='replace') as f:
            json.dump({
                "search_query": search_query,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "number_of_images": len(all_metadata),
                "images": all_metadata
            }, f, indent=4, ensure_ascii=False)
        
        print(f"\nConsolidated metadata saved to: {metadata_path}")
    
    return all_metadata

def process_keyword(keyword: str, limit: int):
    """Process a single keyword search and download."""
    print(f"\n{'='*50}")
    print(f"Processing keyword: '{keyword}'")
    print(f"Requesting {limit} images")
    print(f"{'='*50}")
    
    results = search_wikimedia_commons(keyword, limit)
    
    if results:
        print(f"Found {len(results)} images with captions")
        download_images(results, keyword)
    else:
        print(f"No images found for keyword: {keyword}")

def main():
    parser = argparse.ArgumentParser(
        description='Download images from Wikimedia Commons with variable limits per keyword',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
    1. Different limits for each keyword:
       python image_retrieval_command_args.py "moment of inertia:3" "jet planes:5" "trains:8"

    2. Mix of specified and default limits:
       python image_retrieval_command_args.py "moment of inertia:3" "quantum physics" "trains:8"

    3. Change default limit:
       python image_retrieval_command_args.py -d 10 "moment of inertia:3" "quantum physics" "trains:8"
        """)
    
    parser.add_argument('keyword_limits', nargs='+', 
                       help='Keywords with optional limits (e.g., "keyword:limit" or just "keyword")')
    parser.add_argument('--default', '-d', type=int, default=5,
                      help='Default number of images for keywords without specified limits (default: 5)')
    
    args = parser.parse_args()
    
    # Process each keyword:limit pair
    keyword_pairs = [parse_keyword_limit(kw, args.default) for kw in args.keyword_limits]
    
    print(f"Starting download for {len(keyword_pairs)} keyword(s)")
    print("\nKeyword limits:")
    for keyword, limit in keyword_pairs:
        print(f"- '{keyword}': {limit} images")
    print()
    
    for keyword, limit in keyword_pairs:
        process_keyword(keyword, limit)
    
    print("\nAll downloads completed!")

if __name__ == "__main__":
    main()