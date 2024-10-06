import os
import shutil
import re
import json
from datetime import datetime
import sys

# Define the source directories
source_directory_photos = 'C:\\Users\\sures\\Downloads\\pictures\\less_than_1MB'
source_directory_videos = 'C:\\Users\\sures\\Downloads\\Videos\\less_than_1MB'

# Define the destination directory
destination_directory = 'C:\\Users\\sures\\Downloads\\successful_upload'

# Ensure the destination directory exists
os.makedirs(destination_directory, exist_ok=True)

# Define the directory where the script is located
script_directory = os.path.dirname(os.path.realpath(__file__))

# Define log file paths
activity_log_file = os.path.join(script_directory, f"activity_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
revert_info_file = os.path.join(script_directory, f"revert_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

# Initialize the list for revert information
revert_info = []

# Define image and video file extensions
image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.mpeg'}

# Function to move files and handle duplicates
def move_files(src_dir, filenames):
    for filename in filenames:
        if len(filename) > 0:
            src_file = os.path.join(src_dir, filename)
            dest_file = os.path.join(destination_directory, filename)
            if os.path.exists(src_file):
                original_dest_file = dest_file  # Store the original destination
                # Handle file name conflicts
                if os.path.exists(dest_file):
                    base, ext = os.path.splitext(dest_file)
                    counter = 1
                    new_dest_file = f"{base}_{counter}{ext}"
                    while os.path.exists(new_dest_file):
                        counter += 1
                        new_dest_file = f"{base}_{counter}{ext}"
                    dest_file = new_dest_file
                    log_message = f"Renamed and moved {filename} to {new_dest_file}"
                else:
                    log_message = f"Moved {filename} to {destination_directory}"
                
                shutil.move(src_file, dest_file)
                
                # Log the action
                with open(activity_log_file, 'a') as log_file:
                    log_file.write(log_message + '\n')
                print(log_message)
                
                # Store revert information
                revert_info.append({
                    'source': dest_file,
                    'destination': src_file,
                    'original_destination': original_dest_file
                })
            else:
                log_message = f"File {filename} does not exist in {src_dir}"
                #print(log_message)
                with open(activity_log_file, 'a') as log_file:
                    log_file.write(log_message + '\n')

# Function to revert the file moves
def revert_moves(revert_info_file):
    if os.path.exists(revert_info_file):
        with open(revert_info_file, 'r') as revert_file:
            revert_info = json.load(revert_file)
        for entry in revert_info:
            if os.path.exists(entry['source']):
                print(f"Reverting {entry['source']} to {entry['destination']}")
                shutil.move(entry['source'], entry['destination'])
            else:
                print(f"File {entry['source']} no longer exists and cannot be reverted.")
    else:
        print(f"No revert file found at {revert_info_file}")

# Function to categorize filenames based on their extensions
def categorize_files_by_extension(filenames):
    image_files = []
    video_files = []
    
    for filename in filenames:
        ext = os.path.splitext(filename)[1].lower()  # Get the file extension and normalize case
        if ext in image_extensions:
            image_files.append(filename)
        elif ext in video_extensions:
            video_files.append(filename)
    
    return image_files, video_files

# Main function to either move files or revert based on user input
def main():
    # Ask user for the mode of operation
    mode = input("Enter 'move' to move files or 'revert' to revert the last operation: ").strip().lower()

    if mode == 'move':
        # Find all log files that match the pattern in the script directory
        log_files = [f for f in os.listdir(script_directory) if re.search(r'upload_log_\d+|video_upload_log_\d+', f, re.IGNORECASE)]

        # Check if any log files were found
        if not log_files:
            print("No log files matched the pattern.")
            return
        else:
            print(f"Matched log files: {log_files}")

        filenames = []
        success_files = []

        # Process each log file found
        for log_file in log_files:
            log_file_path = os.path.join(script_directory, log_file)
            with open(log_file_path, 'r') as file:
                content = file.read()
                # Extract filenames based on all provided patterns
                success_files_patterns = [
                    r'Successfully uploaded a group of \d+ (photos|videos):\s*(.*?)\s*(?=INFO|\Z)',
                    r'Successfully uploaded file:\s*(.*?)(?=INFO|\Z)'
                ]
                for pattern in success_files_patterns:
                    matches = re.findall(pattern, content, re.DOTALL)
                    # Depending on the regex, 'matches' might be a list of tuples or strings
                    for match in matches:
                        if isinstance(match, tuple):
                            # In case of a tuple, the second element (filenames) is the one we're interested in
                            file_list = match[1].split(', ')
                        else:
                            file_list = match.split(', ')
                        
                        # Clean each filename by removing newlines, timestamps, or anything after the extension
                        for filename in file_list:
                            cleaned_filename = re.split(r'\s|\n', filename)[0]  # Split by space or newline, keep the first part
                            filenames.append(cleaned_filename.strip())  # Strip any extra whitespace

        # Remove duplicates and ensure filenames are trimmed properly
        filenames = list(set(filenames))
        print(f"Filenames: {filenames}")

        # Categorize files by their extensions (images and videos)
        image_files, video_files = categorize_files_by_extension(filenames)

        # Move image files from the image folder and video files from the video folder
        move_files(source_directory_photos, image_files)
        move_files(source_directory_videos, video_files)

        # Save the revert information
        revert_info = {"moved_files": filenames}
        with open(revert_info_file, 'w') as revert_file:
            json.dump(revert_info, revert_file)

        print(f"All files processed. Total files moved: {len(filenames)}")
        print(f"Activity log saved to {activity_log_file}")
        print(f"Revert info saved to {revert_info_file}")

    elif mode == 'revert':
        revert_moves(revert_info_file)
        print(f"Revert operation completed.")

    else:
        print("Invalid option. Please enter 'move' or 'revert'.")

if __name__ == "__main__":
    main()
