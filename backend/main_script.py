#!/usr/bin/env python3

import subprocess
import sys
import os
from datetime import datetime
import logging
from typing import Optional
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

def setup_logging() -> None:
    """Set up logging configuration"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, f'generation_log_{timestamp}.txt'))
        ]
    )

def flush_message(message: str):
    """Helper function to properly flush messages to stdout"""
    print(message, flush=True)

def run_script(script_name: str, script_description: str) -> Optional[subprocess.CompletedProcess]:
    """Run a Python script and handle its execution"""
    logging.info(f"Starting {script_description}...")
    try:
        # Use flush_message for user-facing updates
        if script_name in ['search_google-1.py', 'vector_search.py']:
            flush_message("Collecting sources from academic and web sources")
        elif script_name == 'outline_writer.py':
            flush_message("Generating article outline based on collected sources")
        elif script_name == 'section_writer_openai.py':
            flush_message("Writing article sections based on outline")
        
        result = subprocess.run(
            [sys.executable, script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        logging.info(f"Successfully completed {script_description}")
        
        # Log the output to file only
        if result.stdout:
            logging.info(f"{script_description} output:\n{result.stdout}")
        
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"Error in {script_description}:\n{e.stderr}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error in {script_description}: {str(e)}")
        raise

def verify_files_exist() -> None:
    """Verify that all required files and directories exist"""
    required_files = [
        'search_google-1.py',
        'outline_writer.py',
        'section_writer_openai.py',
        'topic.txt',
        'vector_search.py'
    ]
    
    required_dirs = [
        'user_profile',
        'style_guide',
        'books',
        'source_html'
    ]
    
    for file in required_files:
        if not os.path.isfile(file):
            raise FileNotFoundError(f"Required file not found: {file}")
    
    for directory in required_dirs:
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Required directory not found: {directory}")
    
    if not os.path.isfile(os.path.join('user_profile', 'User_Profile.txt')):
        raise FileNotFoundError("User_Profile.txt not found in user_profile directory")
    
    if not any(f.endswith('.txt') for f in os.listdir('style_guide')):
        raise FileNotFoundError("No .txt files found in style_guide directory")

def run_parallel_searches() -> bool:
    """Run Google search and vector search in parallel"""
    with ThreadPoolExecutor(max_workers=2) as executor:
        logging.info("Starting parallel search operations...")
        
        flush_message("Collecting sources from academic and web sources")
        
        google_search_future = executor.submit(
            run_script, 'search_google-1.py', 'Google search and content collection'
        )
        vector_search_future = executor.submit(
            run_script, 'vector_search.py', 'Archive vector search'
        )
        
        try:
            logging.info("Waiting for both search operations to complete...")
            
            google_result = google_search_future.result()
            vector_result = vector_search_future.result()
            
            logging.info("Both search operations completed successfully!")
            return True
            
        except Exception as e:
            logging.error(f"Error during parallel search execution: {str(e)}")
            return False

def main() -> None:
    """Main execution function"""
    try:
        setup_logging()
        verify_files_exist()
        
        if not run_parallel_searches():
            raise Exception("Parallel search operations failed")
        
        remaining_scripts = [
            ('outline_writer.py', 'outline generation'),
            ('section_writer_openai.py', 'article writing')
        ]
        
        for script_name, description in remaining_scripts:
            run_script(script_name, description)
        
        logging.info("Article generation completed successfully!")
        logging.info("Article successfully generated and saved to article.md")
        
    except Exception as e:
        logging.error(f"Article generation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()