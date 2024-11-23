from pydantic import BaseModel
from openai import AsyncOpenAI
import json
import os
from pathlib import Path
import asyncio
import platform
import logging
from typing import Optional, Dict, Any
from asyncio import Semaphore
import sys


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fix for Windows event loop
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class ImageSelection(BaseModel):
    saved_filename: str
    explanation: str
    caption: str

async def process_folder(
    folder_path: Path,
    client: AsyncOpenAI,
    semaphore: Semaphore
) -> Optional[Dict[str, Any]]:
    """Process a single folder and select the best image"""
    async with semaphore:  # Limit concurrent API calls
        try:
            # Load metadata from the JSON file
            metadata_path = folder_path / "metadata.json"
            if not metadata_path.exists():
                logger.warning(f"Warning: metadata.json not found in {folder_path}")
                return None

            with open(metadata_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Extract relevant fields
            query = data["query"]
            original_quote = data["original_quote"]
            section_title = data["section_title"]
            reason = data["reason"]
            description = data["description"]
            images = data["images"]

            if not images:
                logger.warning(f"Warning: No images found in metadata for {folder_path}")
                return None

            # Create a single prompt containing all images and context
            content = [
                {"type": "text", "text": f"Context: {original_quote} Reason: {reason} Description: {description}."},
                {"type": "text", "text": "Evaluate the following images to find the best match based on relevance to the context. Favor images with simple structures over complex with loads of text. Return the 'saved_filename' of the best match along with an explanation and a short caption. It's highly possible that no image is a suitable match, please feel free to respond with 'NULL'. Please do not choose images with watermark!"}
            ]

            # Add each image with its filename and URL to the prompt
            for image in images:
                content.append({
                    "type": "text",
                    "text": f"Image filename: {image['saved_filename']}, URL: {image['link']}"
                })

            # Send request to OpenAI
            response = await client.beta.chat.completions.parse(
                model="gpt-4o",
                messages=[{"role": "user", "content": content}],
                response_format=ImageSelection,
                temperature=0,
            )

            # Parse the structured output
            image_selection = response.choices[0].message.parsed

            # If the response is "NULL", return None
            if image_selection.saved_filename == "NULL":
                logger.info(f"No suitable image found for {folder_path}")
                return None

            # Find the selected image metadata from the original data
            selected_image_data = None
            for image in images:
                if image['saved_filename'] == image_selection.saved_filename:
                    selected_image_data = image
                    break

            if not selected_image_data:
                logger.warning(f"Warning: Selected image metadata not found for {image_selection.saved_filename}")
                return None

            # Create the selection result
            selection_result = {
                "original_quote": original_quote,
                "section_title": section_title,
                "reason": reason,
                "description": description,
                "selected_image": {
                    **selected_image_data,
                    "explanation": image_selection.explanation,
                    "caption": image_selection.caption
                }
            }

            # Save the selection result
            selection_path = folder_path / "selected_image.json"
            with open(selection_path, "w", encoding="utf-8") as f:
                json.dump(selection_result, f, indent=2, ensure_ascii=False)

            return selection_result

        except Exception as e:
            logger.error(f"Error processing folder {folder_path}: {str(e)}")
            return None

async def process_all_folders(base_dir: Path, client: AsyncOpenAI):
    """Process all folders concurrently"""
    if not base_dir.exists():
        logger.error(f"Error: Base directory {base_dir} not found!")
        return

    # Get all subdirectories
    subdirs = [d for d in base_dir.iterdir() if d.is_dir()]
    total_folders = len(subdirs)
    
    logger.info(f"\nProcessing {total_folders} folders...")

    # Create semaphore to limit concurrent API calls
    semaphore = Semaphore(5)  # Limit to 5 concurrent API calls

    # Process folders concurrently
    tasks = []
    for folder in subdirs:
        task = process_folder(folder, client, semaphore)
        tasks.append((folder, task))

    # Wait for all tasks to complete and process results
    successful_selections = 0
    failed_selections = 0

    for idx, (folder, task) in enumerate(tasks, 1):
        try:
            result = await task
            
            if result:
                logger.info(f"Successfully selected image for {folder.name}")
                logger.info(f"Selected: {result['selected_image']['saved_filename']}")
                logger.info(f"Caption: {result['selected_image']['caption']}")
                successful_selections += 1
            else:
                logger.warning(f"Failed to select image for {folder.name}")
                failed_selections += 1
                
        except Exception as e:
            logger.error(f"Error processing {folder.name}: {str(e)}")
            failed_selections += 1

    # Print final summary
    logger.info("\nProcessing completed!")
    logger.info(f"Total folders processed: {total_folders}")
    logger.info(f"Successful selections: {successful_selections}")
    logger.info(f"Failed selections: {failed_selections}")

async def main_async():
    # Initialize AsyncOpenAI client
    client = AsyncOpenAI(
        api_key="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"
    )

    # Base directory containing all image search folders
    base_dir = Path("image_searches")

    try:
        await process_all_folders(base_dir, client)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

def main():
    """Entry point that runs the async code"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()