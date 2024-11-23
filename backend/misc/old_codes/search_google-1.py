import requests
from datetime import datetime

def google_search(query: str) -> None:
    """
    Perform a Google Custom Search and save results to a text file
    """
    API_KEY = "AIzaSyDTUZdD1RhA9oey878fzA5o3REMnymR9hk"
    CX = "33f4586468b0c41e6"
    
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': API_KEY,
        'cx': CX,
        'q': query,
        'num': 10  # Number of results (max 10)
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        # Get the search results
        search_results = response.json()
        
        # Create file name with timestamp
        filename = f"google_research_result.txt"
        
        # Open file to write results
        with open(filename, 'w', encoding='utf-8') as f:
            # Write search query and timestamp
            f.write(f"Search Query: {query}\n")
            f.write(f"Search Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 100 + "\n\n")
            
            # Extract and save each result
            if 'items' in search_results:
                for i, item in enumerate(search_results['items'], 1):
                    # Write to console
                    print(f"\n=== Result {i} ===")
                    print(f"Title: {item.get('title', 'N/A')}")
                    print(f"URL: {item.get('link', 'N/A')}")
                    print(f"Description: {item.get('snippet', 'N/A')}\n")
                    print("-" * 100)
                    
                    # Write to file
                    f.write(f"=== Result {i} ===\n")
                    f.write(f"Title: {item.get('title', 'N/A')}\n")
                    f.write(f"URL: {item.get('link', 'N/A')}\n")
                    f.write(f"Description: {item.get('snippet', 'N/A')}\n\n")
                    f.write("-" * 100 + "\n")
            else:
                message = "No results found"
                print(message)
                f.write(message + "\n")
                
        print(f"\nResults have been saved to {filename}")
            
    except requests.exceptions.RequestException as e:
        error_message = f"Error making request: {e}"
        print(error_message)
        with open('google_search_error.txt', 'w', encoding='utf-8') as f:
            f.write(error_message)
    except Exception as e:
        error_message = f"An error occurred: {e}"
        print(error_message)
        with open('google_search_error.txt', 'w', encoding='utf-8') as f:
            f.write(error_message)

# Test the search
if __name__ == "__main__":
    search_query = input("Enter your search query: ")
    google_search(search_query)