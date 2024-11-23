#!/usr/bin/env python3
import numpy as np
import pickle
import os
from openai import OpenAI
from typing import List, Tuple, Dict
import glob
from datetime import datetime

def load_all_vectors(base_dir: str) -> Dict[str, Tuple[np.ndarray, list]]:
    """Load pre-computed embeddings and chunks from all subfolders"""
    print("Loading vectors and chunks from all books...")
    book_data = {}
    
    # Get all subdirectories in the books folder
    book_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    for book_dir in book_dirs:
        full_path = os.path.join(base_dir, book_dir)
        embeddings_path = os.path.join(full_path, "embeddings.npy")
        chunks_path = os.path.join(full_path, "chunks.pkl")
        
        # Skip if either file doesn't exist
        if not (os.path.exists(embeddings_path) and os.path.exists(chunks_path)):
            print(f"Skipping {book_dir} - missing required files")
            continue
            
        try:
            embeddings = np.load(embeddings_path)
            with open(chunks_path, 'rb') as f:
                chunks = pickle.load(f)
            print(f"Loaded {len(chunks)} chunks from {book_dir}")
            book_data[book_dir] = (embeddings, chunks)
        except Exception as e:
            print(f"Error loading {book_dir}: {str(e)}")
            continue
    
    return book_data

def search_all_books(query: str, book_data: Dict[str, Tuple[np.ndarray, list]], n_results: int = 5) -> Dict[str, List[Tuple[str, float]]]:
    """Search for most similar chunks across all books"""
    # Get embedding for the query
    client = OpenAI(api_key="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")
    query_response = client.embeddings.create(
        input=[query],
        model="text-embedding-3-small"
    )
    query_embedding = np.array(query_response.data[0].embedding)
    
    results_by_book = {}
    
    for book_name, (embeddings, chunks) in book_data.items():
        # Compute cosine similarities
        query_norm = np.linalg.norm(query_embedding)
        embeddings_norm = np.linalg.norm(embeddings, axis=1)
        similarities = np.dot(embeddings, query_embedding) / (embeddings_norm * query_norm)
        
        # Get top results for this book
        top_indices = np.argsort(similarities)[-n_results:][::-1]
        
        # Store results with scores
        results_by_book[book_name] = [(chunks[idx], float(similarities[idx])) for idx in top_indices]
    
    return results_by_book

def save_results_to_html(query: str, results_by_book: Dict[str, List[Tuple[str, float]]], output_path: str):
    """Save search results to an HTML file"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vector Search Results</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .book-section {{ margin-bottom: 30px; }}
            .result {{ margin-bottom: 20px; padding: 15px; background-color: #f9f9f9; border-radius: 5px; }}
            .score {{ color: #666; font-size: 0.9em; }}
            .note {{ color: #888; font-style: italic; margin-top: 20px; }}
            .query {{ background-color: #e9e9e9; padding: 10px; margin-bottom: 20px; border-radius: 5px; }}
            .timestamp {{ color: #888; font-size: 0.8em; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h1>Vector Search Results</h1>
        <div class="timestamp">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        <div class="query">Search Query: {query}</div>
    """
    
    for book_name, results in results_by_book.items():
        html_content += f"""
        <div class="book-section">
            <h2>Results from: {book_name}</h2>
        """
        
        for i, (chunk, score) in enumerate(results, 1):
            html_content += f"""
            <div class="result">
                <h3>Result {i}</h3>
                <p>{chunk.strip()}</p>
                <div class="score">Similarity Score: {score:.3f}</div>
            </div>
            """
        
        html_content += "</div>"
    
    html_content += """
        <div class="note">These are vector search results from our archive! These might not be totally related, but use them at your discretion.</div>
    </body>
    </html>
    """
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Results saved to {output_path}")

def main():
    # Get the directory where the script is located
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths relative to script location
    BOOKS_DIR = os.path.join(SCRIPT_DIR, "books")
    TOPIC_PATH = os.path.join(SCRIPT_DIR, "topic.txt")
    OUTPUT_PATH = os.path.join(SCRIPT_DIR, "source_html", "topic_archive.html")
    
    # Load vectors from all books
    book_data = load_all_vectors(BOOKS_DIR)
    
    if not book_data:
        print("No valid book data found!")
        return
    
    # Read search query from topic.txt
    try:
        with open(TOPIC_PATH, 'r', encoding='utf-8') as f:
            query = f.read().strip()
    except FileNotFoundError:
        print(f"Error: topic.txt not found at {TOPIC_PATH}")
        return
    except Exception as e:
        print(f"Error reading topic.txt: {str(e)}")
        return
    
    if not query:
        print("Error: topic.txt is empty")
        return
    
    print(f"\nSearching for: {query}")
    results_by_book = search_all_books(query, book_data)
    
    # Save results to HTML
    save_results_to_html(query, results_by_book, OUTPUT_PATH)

if __name__ == "__main__":
    main()