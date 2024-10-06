import os
import shutil
import logging
from datetime import datetime
from PIL import Image
import pytesseract
from concurrent.futures import ThreadPoolExecutor, as_completed

# =========================
# Configuration Parameters
# =========================

# Set path to Tesseract executable if it's not already in your PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define the list of input directories containing the images and other files
input_directories = [
    r'C:\Users\sures\Downloads\Telegram Desktop'
    # Add more directories as needed
]

# Define the output directory where categorized folders will be created
output_directory = r'C:\Users\sures\Downloads\Final'

# Define the subfolder for images containing text (under 'pictures')
text_images_directory = os.path.join(output_directory, 'pictures', 'textimages')

# Define the size categories in MB
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

# Define the file extensions for videos and pictures
video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.mpeg']
picture_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']

# Define the base directories for video, picture, and others within the output directory
BASE_VIDEO_DIR = 'videos'
BASE_PICTURE_DIR = 'pictures'
BASE_OTHERS_DIR = 'others'

# =========================
# Logging Setup
# =========================

def setup_logging(log_directory):
    """
    Sets up logging for the script with UTF-8 encoding to handle Unicode characters.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_directory, f'process_log_{timestamp}.log')
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'  # Ensure UTF-8 encoding
    )
    return log_file

# =========================
# Utility Functions
# =========================

def create_directories(base_path):
    """
    Creates the necessary subdirectories within the output directory based on size categories.
    """
    # Create size-based directories for videos and pictures
    for _, folder in size_categories:
        video_path = os.path.join(base_path, BASE_VIDEO_DIR, folder)
        picture_path = os.path.join(base_path, BASE_PICTURE_DIR, folder)
        os.makedirs(video_path, exist_ok=True)
        os.makedirs(picture_path, exist_ok=True)
    
    # Create 'others' directory
    others_path = os.path.join(base_path, BASE_OTHERS_DIR)
    os.makedirs(others_path, exist_ok=True)
    
    # Create 'textimages' directory under 'pictures'
    os.makedirs(text_images_directory, exist_ok=True)

def get_size_category(file_size):
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

def image_contains_text(image_path):
    """
    Checks if an image contains any text using OCR.
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        if text.strip():
            return True
    except Exception as e:
        logging.error(f"Error processing image {image_path}: {e}")
    return False

# =========================
# Main Processing Function
# =========================

def main():
    # === Setup Logging ===
    log_directory = output_directory  # Logs will be stored in the output directory

    # === Create Necessary Directories ===
    create_directories(output_directory)
    logging.info("Created necessary directories.")

    log_file = setup_logging(log_directory)
    logging.info("Script started.")

    # === Collect All Files from Input Directories ===
    all_files = []
    for input_dir in input_directories:
        if not os.path.exists(input_dir):
            logging.warning(f"Input directory does not exist: {input_dir}")
            print(f"Input directory does not exist: {input_dir}")
            continue
        for root, _, files in os.walk(input_dir):
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)
    logging.info(f"Total files found: {len(all_files)}")
    print(f"Total files found: {len(all_files)}")

    # === Initialize Counters for Summary ===
    summary = {
        'textimages': 0,
        'videos': {},
        'pictures': {},
        'others': 0,
        'failed_moves': 0
    }

    # Initialize size categories counters for videos and pictures
    for _, category in size_categories:
        summary['videos'][category] = 0
        summary['pictures'][category] = 0

    # === Categorize and Move All Files ===
    print("Starting file categorization and moving process...")
    logging.info("Starting file categorization and moving process.")

    images_to_process_for_text = []  # To keep track of images in 'pictures' for OCR

    for file_path in all_files:
        file_extension = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        size_category = get_size_category(file_size)
        filename = os.path.basename(file_path)

        if file_extension in video_extensions:
            dest_folder = os.path.join(output_directory, BASE_VIDEO_DIR, size_category)
            dest_path = os.path.join(dest_folder, filename)
            moved = move_file(file_path, dest_path)
            if moved:
                summary['videos'][size_category] += 1
            else:
                summary['failed_moves'] += 1

        elif file_extension in picture_extensions:
            width, height = get_image_resolution(file_path)
            if width is not None and height is not None and (width > 1000 or height > 1000):
                dest_folder = os.path.join(output_directory, BASE_PICTURE_DIR, size_category)
                images_to_process_for_text.append(os.path.join(dest_folder, filename))  # Track moved images
            else:
                dest_folder = os.path.join(output_directory, BASE_OTHERS_DIR)
            dest_path = os.path.join(dest_folder, filename)
            moved = move_file(file_path, dest_path)
            if moved:
                if dest_folder.startswith(os.path.join(output_directory, BASE_PICTURE_DIR)):
                    summary['pictures'][size_category] += 1
                    images_to_process_for_text.append(dest_path)  # Add to list for OCR
                else:
                    summary['others'] += 1
            else:
                summary['failed_moves'] += 1

        else:
            dest_folder = os.path.join(output_directory, BASE_OTHERS_DIR)
            dest_path = os.path.join(dest_folder, filename)
            moved = move_file(file_path, dest_path)
            if moved:
                summary['others'] += 1
            else:
                summary['failed_moves'] += 1

    logging.info("File categorization and moving completed.")

    # === Process Images in 'pictures' for Text Detection ===
    print("\nStarting OCR processing on images in 'pictures' directory...")
    logging.info("Starting OCR processing on images in 'pictures' directory.")

    # Gather all images in 'pictures' subfolders
    pictures_base_path = os.path.join(output_directory, BASE_PICTURE_DIR)
    images_for_ocr = []
    for root, _, files in os.walk(pictures_base_path):
        for file in files:
            if os.path.splitext(file)[1].lower() in picture_extensions:
                image_path = os.path.join(root, file)
                images_for_ocr.append(image_path)

    logging.info(f"Total images to process for OCR: {len(images_for_ocr)}")
    print(f"Total images to process for OCR: {len(images_for_ocr)}")

    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = {executor.submit(image_contains_text, image_path): image_path for image_path in images_for_ocr}
        for future in as_completed(futures):
            image_path = futures[future]
            try:
                has_text = future.result()
                if has_text:
                    # Move to pictures/textimages directory
                    filename = os.path.basename(image_path)
                    dest_path = os.path.join(text_images_directory, filename)
                    moved = move_file(image_path, dest_path)
                    if moved:
                        summary['textimages'] += 1
            except Exception as e:
                logging.error(f"Error processing OCR for {image_path}: {e}")
                summary['failed_moves'] += 1

    logging.info("OCR processing completed.")

    # === Summary of Operations ===
    print("\n=== Summary of Categorization ===")
    logging.info("Summary of Categorization:")
    total_moved = summary['textimages'] + sum(summary['videos'].values()) + sum(summary['pictures'].values()) + summary['others']
    total_failed = summary['failed_moves']
    print(f"Total files moved: {total_moved}")
    logging.info(f"Total files moved: {total_moved}")

    print(f" - Images with text: {summary['textimages']}")
    logging.info(f" - Images with text: {summary['textimages']}")

    print(" - Videos:")
    logging.info(" - Videos:")
    for category, count in summary['videos'].items():
        print(f"    {category}: {count}")
        logging.info(f"    {category}: {count}")

    print(" - Pictures:")
    logging.info(" - Pictures:")
    for category, count in summary['pictures'].items():
        print(f"    {category}: {count}")
        logging.info(f"    {category}: {count}")

    print(f" - Others: {summary['others']}")
    logging.info(f" - Others: {summary['others']}")

    print(f"Total files failed to move: {total_failed}")
    logging.info(f"Total files failed to move: {total_failed}")

    logging.info("Script completed.")

if __name__ == "__main__":
    main()
