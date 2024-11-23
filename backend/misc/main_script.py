import subprocess
import sys
import os
from datetime import datetime
import logging
from typing import Optional

def setup_logging() -> None:
    """Set up logging configuration"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, f'generation_log_{timestamp}.txt')),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_script(script_name: str, script_description: str) -> Optional[subprocess.CompletedProcess]:
    """Run a Python script and handle its execution"""
    logging.info(f"Starting {script_description}...")
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info(f"Successfully completed {script_description}")
        
        # Log the output
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
        'Search_google-1.py',
        'outline_writer.py',
        'section_writer_openai.py',
        'topic.txt'
    ]
    
    required_dirs = [
        'user_profile',
        'style_guide'
    ]
    
    # Check files
    for file in required_files:
        if not os.path.isfile(file):
            raise FileNotFoundError(f"Required file not found: {file}")
    
    # Check directories
    for directory in required_dirs:
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Required directory not found: {directory}")
    
    # Check specific required files in directories
    if not os.path.isfile(os.path.join('user_profile', 'User_Profile.txt')):
        raise FileNotFoundError("User_Profile.txt not found in user_profile directory")
    
    # Check if style_guide directory has at least one .txt file
    if not any(f.endswith('.txt') for f in os.listdir('style_guide')):
        raise FileNotFoundError("No .txt files found in style_guide directory")

def main() -> None:
    """Main execution function"""
    try:
        # Set up logging
        setup_logging()
        
        # Verify all required files exist
        verify_files_exist()
        
        # Execute scripts in sequence
        scripts = [
            ('Search_google-1.py', 'Google search and content collection'),
            ('outline_writer.py', 'outline generation'),
            ('section_writer_openai.py', 'article writing')
        ]
        
        for script_name, description in scripts:
            run_script(script_name, description)
        
        logging.info("Article generation completed successfully!")
        logging.info("Article successfully generated and saved to article.md")
    except Exception as e:
        logging.error(f"Article generation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
