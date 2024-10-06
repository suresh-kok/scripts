# utils/file_categorizer.py

import os
import shutil
import logging
from PIL import Image

def get_size_category(file_size, size_categories):
    """
    Determines the size category of a file based on its size in bytes.
    """
    size_in_mb = file_size / (1024 * 1024)
    for size, category in size_categories:
        if size_in_mb < size:
            return category
    return 'greater_than_30MB'

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

def categorize_and_move(file_path, base_path, size_categories, video_extensions, picture_extensions):
    """
    Categorizes a single file based on its type and size, then moves it to the appropriate directory.
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    file_size = os.path.getsize(file_path)
    size_category = get_size_category(file_size, size_categories)
    filename = os.path.basename(file_path)

    if file_extension in video_extensions:
        dest_folder = os.path.join(base_path, 'videos', size_category)
    elif file_extension in picture_extensions:
        width, height = get_image_resolution(file_path)
        if width is not None and height is not None and (width > 1000 or height > 1000):
            dest_folder = os.path.join(base_path, 'pictures', size_category)
        else:
            dest_folder = os.path.join(base_path, 'others')
    else:
        dest_folder = os.path.join(base_path, 'others')

    os.makedirs(dest_folder, exist_ok=True)
    dest_path = os.path.join(dest_folder, filename)

    success = move_file(file_path, dest_path)
    return success, dest_folder

def categorize_files(all_files, base_path, size_categories, video_extensions, picture_extensions, max_workers=25):
    """
    Categorizes and moves all files based on type and size.
    Returns counts of moved files and failed moves.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    moved_count = 0
    failed_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(categorize_and_move, file_path, base_path, size_categories, video_extensions, picture_extensions): file_path for file_path in all_files}
        
        for future in as_completed(futures):
            file_path = futures[future]
            try:
                success, dest_folder = future.result()
                if success:
                    moved_count += 1
                    logging.info(f"Successfully moved: {file_path} to {dest_folder}")
                else:
                    failed_count += 1
                    logging.error(f"Failed to move: {file_path}")
            except Exception as e:
                failed_count += 1
                logging.error(f"Error categorizing {file_path}: {e}")

    return moved_count, failed_count
