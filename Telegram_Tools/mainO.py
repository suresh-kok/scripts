# main.py

import logging
import os
from utils.logging_utils import setup_logging
from utils.file_mover import find_latest_log, extract_file_paths_from_log, move_files
from utils.ocr_processor import image_contains_text, process_images
from utils.file_categorizer import categorize_files

def main():
    # === Configuration ===
    # Directories
    log_directory = r'C:\Users\sures\OneDrive\Desktop\scripts\Telegram_Tools\Send_Messages'
    log_pattern = 'successful_uploads_*.log'
    destination_directory = r'C:\Users\sures\Downloads\successful_upload'
    images_directory = r'C:\Users\sures\Downloads\pictures\less_than_1MB'
    text_images_directory = os.path.join(destination_directory, 'pictures', 'textimages')
    
    # File categorization parameters
    size_categories = [
        (1, 'less_than_1MB'),
        (2, 'less_than_2MB'),
        (3, 'less_than_3MB'),
        (5, 'less_than_5MB'),
        (8, 'less_than_8MB'),
        (10, 'less_than_10MB'),
        (15, 'less_than_15MB'),
        (20, 'less_than_20MB'),
        (25, 'less_than_25MB'),
        (30, 'less_than_30MB'),
        (float('inf'), 'greater_than_30MB')  # Handle files larger than 30MB
    ]
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.mpeg']
    picture_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
    
    # === Setup Logging ===
    log_file = setup_logging(log_directory)
    print(f"Logging initialized. Log file: {log_file}")
    
    # === Process Log and Move Files ===
    latest_log = find_latest_log(log_directory, log_pattern)
    if latest_log:
        print(f"Using log file: {latest_log}")
        file_paths = extract_file_paths_from_log(latest_log)
        moved_count, failed_count = move_files(file_paths, destination_directory)
        print(f"Files moved from log: {moved_count}, Failed moves: {failed_count}")
    else:
        print("No successful upload log files found.")
    
    # === Process Images for Text Detection ===
    # Gather image files
    image_files = [os.path.join(images_directory, filename) for filename in os.listdir(images_directory) 
                   if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]
    
    print(f"Total image files to process for OCR: {len(image_files)}")
    logging.info(f"Total image files to process for OCR: {len(image_files)}")
    
    # Process images and move those with text
    images_with_text = process_images(image_files, text_images_directory, max_workers=25)
    
    # === Categorize and Move Remaining Files ===
    # Exclude images that have been moved
    remaining_files = [f for f in file_paths if f not in images_with_text]
    
    moved_count_cat, failed_count_cat = categorize_files(
        remaining_files,
        destination_directory,
        size_categories,
        video_extensions,
        picture_extensions,
        max_workers=25
    )
    
    print(f"Files categorized and moved: {moved_count_cat}, Failed moves: {failed_count_cat}")
    
    # === Final Summary ===
    total_moved = moved_count + moved_count_cat
    total_failed = failed_count + failed_count_cat
    logging.info(f"Total files moved: {total_moved}, Total failed moves: {total_failed}")
    print(f"All operations completed. Total files moved: {total_moved}, Total failed moves: {total_failed}")

if __name__ == '__main__':
    main()
