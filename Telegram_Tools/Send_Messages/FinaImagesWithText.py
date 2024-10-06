import os
from PIL import Image
import pytesseract
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set path to tesseract executable if it's not already in your PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define the directory containing the images
images_directory = r'C:\Users\sures\Downloads\pictures\less_than_1MB'

# Define the subfolder for images containing text
text_images_directory = os.path.join(images_directory, 'textimages')

# Ensure the subfolder exists
os.makedirs(text_images_directory, exist_ok=True)

# Define a list to store the images that contain text
images_with_text = []

# Function to check if an image contains text
def image_contains_text(image_path):
    try:
        # Open the image using Pillow
        img = Image.open(image_path)

        # Use pytesseract to extract text from the image
        text = pytesseract.image_to_string(img)

        # Strip the text to remove invisible characters and check if it's non-empty
        if text.strip():
            return image_path
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
    
    return None

# Function to move images with text
def move_image_with_text(image_path):
    if image_path:
        filename = os.path.basename(image_path)
        destination_path = os.path.join(text_images_directory, filename)
        shutil.move(image_path, destination_path)
        print(f"Moved {filename} to {text_images_directory}")
        return filename
    return None

# Get the list of all image files
image_files = [os.path.join(images_directory, filename) for filename in os.listdir(images_directory) 
               if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]

# Use ThreadPoolExecutor to process 10 images at a time
with ThreadPoolExecutor(max_workers=25) as executor:
    # Submit tasks to check for text in each image
    futures = {executor.submit(image_contains_text, image_path): image_path for image_path in image_files}

    # Process completed tasks
    for future in as_completed(futures):
        image_with_text = future.result()
        if image_with_text:
            # If text is found, move the image
            moved_image = move_image_with_text(image_with_text)
            if moved_image:
                images_with_text.append(moved_image)

# Output the list of images that contain text
print("\nImages with text:")
for image in images_with_text:
    print(image)
