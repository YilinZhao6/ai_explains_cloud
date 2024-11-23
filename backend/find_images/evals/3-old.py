from pydantic import BaseModel
from openai import OpenAI
import json

# Initialize OpenAI client
client = OpenAI(api_key="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")

# Load metadata from the JSON file
with open("metadata.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Extract relevant fields
query = data["query"]
original_quote = data["original_quote"]
reason = data["reason"]
description = data["description"]
images = data["images"]

# Pydantic model for structured output
class ImageSelection(BaseModel):
    saved_filename: str
    explanation: str
    caption: str

# Create a single prompt containing all images and context
content = [
    {"type": "text", "text": f"Context: {original_quote} Reason: {reason} Description: {description}."},
    {"type": "text", "text": "Evaluate the following images to find the best match based on relevance to the context. Return the 'saved_filename' of the best match along with an explanation and a short caption. If no image is a suitable match, respond with 'NULL'.Please do not choose images with watermark!"}
]

# Add each image with its filename and URL to the prompt
for image in images:
    content.append({
        "type": "text",
        "text": f"Image filename: {image['saved_filename']}, URL: {image['link']}"
    })

# Send all images in a single request to let the model choose
response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[{"role": "user", "content": content}],
    response_format=ImageSelection
)

# Parse the structured output
image_selection = response.choices[0].message.parsed

# If the response is "NULL", interpret it appropriately
if image_selection.saved_filename == "NULL":
    image_selection.saved_filename = None
    image_selection.explanation = "NULL"

# Display the result as structured JSON
print(image_selection.json(indent=2))
