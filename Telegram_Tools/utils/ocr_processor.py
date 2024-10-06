# utils/ocr_processor.py

import os
import shutil
import logging
from PIL import Image
import pytesseract
from concurrent.futures import ThreadPoolExecutor, as_completed

def image_contains_text(image_path):
    """
    Checks if an image contains any text using OCR.
    Returns True if text is found, False otherwise.
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        if text.strip():
            return True
    except Exception as e:
        logging.error(f"Error processing image {image_path}: {e}")
    return False

def get_image_resolution(file_path):
    """
    Retrieves the resolution (width and height) of an image.
    """
    try:
        with Image.open(file_path) as img:
            return img.width, img.height
    except Exception as e:
        logging.error(f"Error getting resolution for {file_path}: {e}")
        return None, None

def process_images(image_files, text_images_directory, max_workers=25):
    """
    Processes images to detect text using OCR and moves images containing text to text_images_directory.
    Returns the list of moved images.
    """
    os.makedirs(text_images_directory, exist_ok=True)
    images_with_text = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(image_contains_text, image_path): image_path for image_path in image_files}
        
        for future in as_completed(futures):
            image_path = futures[future]
            try:
                has_text = future.result()
                if has_text:
                    filename = os.path.basename(image_path)
                    dest_path = os.path.join(text_images_directory, filename)
                    moved = move_file(image_path, dest_path)
                    if moved:
                        images_with_text.append(image_path)
                        logging.info(f"Moved {filename} to {text_images_directory}")
                        print(f"Moved: {filename} to {text_images_directory}")
            except Exception as e:
                logging.error(f"Error processing OCR for {image_path}: {e}")
                print(f"Error processing {os.path.basename(image_path)}: {e}")
    
    return images_with_text

def move_file(src_path, dest_path):
    """
    Moves a file from src_path to dest_path, handling duplicates by appending a counter.
    Returns True if moved successfully, False otherwise.
    """
    original_dest_path = dest_path
    counter = 1
    while os.path.exists(dest_path):
        file_name, file_extension = os.path.splitext(os.path.basename(original_dest_path))
        dest_path = os.path.join(os.path.dirname(original_dest_path), f"{file_name}_{counter}{file_extension}")
        counter += 1
    try:
        shutil.move(src_path, dest_path)
        logging.info(f"Moved {src_path} to {dest_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to move {src_path} to {dest_path}. Error: {e}")
        return False
