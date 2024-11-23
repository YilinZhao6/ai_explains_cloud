import requests
import os
import json
import urllib.parse
from typing import List, Dict
import time

# Define headers with a proper User-Agent
HEADERS = {
    'User-Agent': 'WikimediaImageDownloader/1.0 (https://github.com/yourusername; your@email.com) Python/3.x'
}

def search_wikimedia_commons(query: str, limit: int = 10) -> List[Dict]:
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
            print("No results found.")
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
                "thumb_url": info.get("thumburl", ""),  # Also get thumbnail URL as backup
                "width": info.get("width", 0),
                "height": info.get("height", 0),
                "size": info.get("size", 0),
                "mime": info.get("mime", ""),
                "commons_url": page.get("canonicalurl", "")
            }
            results.append(result)
            
        return results
    
    except Exception as e:
        print(f"Error searching Wikimedia Commons: {str(e)}")
        return []

def download_images(results: List[Dict], output_dir: str = "commons_images") -> None:
    """Download images and save their metadata."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for idx, result in enumerate(results, 1):
        # Create safe filename
        base_filename = result["title"]
        safe_filename = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in base_filename)
        
        # Get file extension
        ext = result["mime"].split("/")[-1] if result["mime"] else result["url"].split(".")[-1]
        image_filename = f"{safe_filename}.{ext}"
        json_filename = f"{safe_filename}.json"
        
        try:
            print(f"\nDownloading {idx}/{len(results)}: {result['title']}")
            
            # Try to download the full resolution image
            response = requests.get(result["url"], headers=HEADERS, stream=True)
            
            if response.status_code == 200:
                image_path = os.path.join(output_dir, image_filename)
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
                    "local_path": os.path.abspath(image_path)
                }
                
                json_path = os.path.join(output_dir, json_filename)
                with open(json_path, 'w', encoding='utf-8', errors='replace') as f:
                    json.dump(metadata, f, indent=4, ensure_ascii=False)
                
                print(f"Successfully downloaded: {image_filename}")
                print(f"Description: {result['description'][:100]}...")
                
            else:
                print(f"Failed to download image: HTTP {response.status_code}")
                print("Skipping this image.")
                
        except Exception as e:
            print(f"Error downloading {result['title']}: {str(e)}")
        
        # Small delay between downloads
        time.sleep(1)

def main(query: str, limit: int = 10):
    print(f"Searching Wikimedia Commons for '{query}'...")
    results = search_wikimedia_commons(query, limit)
    
    if not results:
        print("No images found with captions.")
        return
    
    print(f"\nFound {len(results)} images with captions")
    download_images(results)
    print("\nDownload complete!")

if __name__ == "__main__":
    query = "moment of inertia"
    main(query, limit=10)