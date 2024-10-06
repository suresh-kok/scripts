import os
import shutil
from PIL import Image

# Define the base directories for video, picture, and others
BASE_VIDEO_DIR = 'videos'
BASE_PICTURE_DIR = 'pictures'
BASE_OTHERS_DIR = 'others'

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
picture_extensions = ['.jpg', '.jpeg', '.png', '.bmp']

def create_directories(base_path):
    for _, folder in size_categories:
        video_path = os.path.join(base_path, BASE_VIDEO_DIR, folder)
        picture_path = os.path.join(base_path, BASE_PICTURE_DIR, folder)
        os.makedirs(video_path, exist_ok=True)
        os.makedirs(picture_path, exist_ok=True)
    others_path = os.path.join(base_path, BASE_OTHERS_DIR)
    os.makedirs(others_path, exist_ok=True)

def get_size_category(file_size):
    size_in_mb = file_size / (1024 * 1024)
    for size, category in size_categories:
        if size_in_mb < size:
            return category
    return 'greater_than_30MB'

def get_image_resolution(file_path):
    try:
        with Image.open(file_path) as img:
            return img.width, img.height
    except Exception:
        return None, None

def move_file(file_path, base_path):
    file_size = os.path.getsize(file_path)
    size_category = get_size_category(file_size)
    file_extension = os.path.splitext(file_path)[1].lower()
    file_name = os.path.basename(file_path)

    # Check if the file name ends with _thumb.jpg
    if file_name.endswith('_thumb.jpg'):
        destination_folder = os.path.join(base_path, BASE_OTHERS_DIR)
    elif file_extension in video_extensions:
        destination_folder = os.path.join(base_path, BASE_VIDEO_DIR, size_category)
    elif file_extension in picture_extensions:
        width, height = get_image_resolution(file_path)
        if width is not None and height is not None and (width > 1000 or height > 1000):
            destination_folder = os.path.join(base_path, BASE_PICTURE_DIR, size_category)
        else:
            destination_folder = os.path.join(base_path, BASE_OTHERS_DIR)
    else:
        destination_folder = os.path.join(base_path, BASE_OTHERS_DIR)

    destination_path = os.path.join(destination_folder, file_name)
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)  # Ensure the destination folder exists

    # Handle duplicates by appending a number to the filename
    original_destination_path = destination_path
    counter = 1
    while os.path.exists(destination_path):
        file_name, file_extension = os.path.splitext(os.path.basename(original_destination_path))
        destination_path = os.path.join(destination_folder, f"{file_name}_{counter}{file_extension}")
        counter += 1

    shutil.move(file_path, destination_path)
    print(f'Moved {file_path} to {destination_path}')

def traverse_and_categorize_files(base_path):
    for root, dirs, files in os.walk(base_path):
        if root.startswith(os.path.join(base_path, BASE_VIDEO_DIR)) or root.startswith(os.path.join(base_path, BASE_PICTURE_DIR)) or root.startswith(os.path.join(base_path, BASE_OTHERS_DIR)):
            continue
        
        for file in files:
            file_path = os.path.join(root, file)
            move_file(file_path, base_path)

if __name__ == "__main__":
    base_directory = 'C:\\Users\\sures\\Downloads\\Telegram Desktop' 
    create_directories(base_directory)
    traverse_and_categorize_files(base_directory)
