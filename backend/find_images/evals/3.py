from pydantic import BaseModel
from openai import OpenAI
import json
import os
from pathlib import Path

class ImageSelection(BaseModel):
    saved_filename: str
    explanation: str
    caption: str

def process_folder(folder_path: Path, client: OpenAI) -> dict:
    """Process a single folder and select the best image"""
    try:
        # Load metadata from the JSON file
        metadata_path = folder_path / "metadata.json"
        if not metadata_path.exists():
            print(f"Warning: metadata.json not found in {folder_path}")
            return None

        with open(metadata_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Extract relevant fields
        query = data["query"]
        original_quote = data["original_quote"]
        section_title = data["section_title"]  # Added section_title
        reason = data["reason"]
        description = data["description"]
        images = data["images"]

        if not images:
            print(f"Warning: No images found in metadata for {folder_path}")
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
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[{"role": "user", "content": content}],
            response_format=ImageSelection,
            temperature=0,
        )

        # Parse the structured output
        image_selection = response.choices[0].message.parsed

        # If the response is "NULL", return None
        if image_selection.saved_filename == "NULL":
            print(f"No suitable image found for {folder_path}")
            return None

        # Find the selected image metadata from the original data
        selected_image_data = None
        for image in images:
            if image['saved_filename'] == image_selection.saved_filename:
                selected_image_data = image
                break

        if not selected_image_data:
            print(f"Warning: Selected image metadata not found for {image_selection.saved_filename}")
            return None

        # Create the selection result
        selection_result = {
            "original_quote": original_quote,
            "section_title": section_title,  # Added section_title to the result
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
        print(f"Error processing folder {folder_path}: {str(e)}")
        return None

def main():
    # Initialize OpenAI client
    client = OpenAI(api_key="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")

    # Base directory containing all image search folders
    base_dir = Path("image_searches")
    
    if not base_dir.exists():
        print(f"Error: Base directory {base_dir} not found!")
        return

    # Get all subdirectories
    subdirs = [d for d in base_dir.iterdir() if d.is_dir()]
    total_folders = len(subdirs)
    successful_selections = 0
    failed_selections = 0

    print(f"\nProcessing {total_folders} folders...")

    # Process each subfolder
    for idx, folder in enumerate(subdirs, 1):
        print(f"\nProcessing folder {idx}/{total_folders}: {folder.name}")
        
        result = process_folder(folder, client)
        
        if result:
            print(f"Successfully selected image for {folder.name}")
            print(f"Selected: {result['selected_image']['saved_filename']}")
            print(f"Caption: {result['selected_image']['caption']}")
            successful_selections += 1
        else:
            print(f"Failed to select image for {folder.name}")
            failed_selections += 1

    # Print final summary
    print("\nProcessing completed!")
    print(f"Total folders processed: {total_folders}")
    print(f"Successful selections: {successful_selections}")
    print(f"Failed selections: {failed_selections}")

if __name__ == "__main__":
    main()
