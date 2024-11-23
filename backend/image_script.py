import subprocess
import os
import shutil
from pathlib import Path
import sys
import time
import sys


def run_script(script_name, working_dir):
    """
    Run a Python script and stream its output in real time
    """
    process = subprocess.Popen(
        [sys.executable, script_name],
        cwd=working_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    # Print output in real time
    for line in process.stdout:
        print(f"[{script_name}] {line.rstrip()}")
    
    # Wait for the process to complete
    process.wait()
    
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, script_name)

def main():
    # Define paths
    current_dir = Path.cwd()
    find_images_dir = current_dir / "find_images"
    article_path = current_dir / "article.md"
    updated_article_path = find_images_dir / "updated_article.md"
    
    # Check if article.md exists
    if not article_path.exists():
        print("Error: article.md not found in the current directory!")
        return
    
    # Copy article.md to find_images directory
    print("\nCopying article.md to find_images directory...")
    shutil.copy2(article_path, find_images_dir / "article.md")
    
    # List of scripts to run in order
    scripts = ["1.py", "2.py", "3.py", "4.py"]
    
    # Run each script in sequence
    for script in scripts:
        print(f"\n{'='*50}")
        print(f"Running {script}...")
        print(f"{'='*50}\n")
        
        try:
            run_script(script, find_images_dir)
            print(f"\nSuccessfully completed {script}")
            # Add a small delay between scripts
            time.sleep(1)
            
        except subprocess.CalledProcessError as e:
            print(f"\nError running {script}: Process returned code {e.returncode}")
            return
        except Exception as e:
            print(f"\nUnexpected error running {script}: {str(e)}")
            return
    
    # Copy updated_article.md back to main directory if it exists
    if updated_article_path.exists():
        print("\nCopying updated_article.md back to main directory...")
        shutil.copy2(updated_article_path, current_dir / "updated_article.md")
        print("Pipeline completed successfully!")
    else:
        print("\nWarning: updated_article.md not found in find_images directory!")

if __name__ == "__main__":
    main()