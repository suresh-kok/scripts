import os
import shutil
import re

# Define the source directory and the destination directory
source_directory = 'C:\\Users\\sures\\Downloads\\pictures\\less_than_1MB'
destination_directory = 'C:\\Users\\sures\\Downloads\\successful_upload'

# Ensure the destination directory exists
os.makedirs(destination_directory, exist_ok=True)

# Define the log file path
log_file_path = r'C:\Users\sures\OneDrive\Desktop\scripts\Telegram_Tools\Send_Messages\upload_log_20240911_204514.log'

# Read the log file and extract filenames
filenames = []
with open(log_file_path, 'r') as file:
    content = file.read()

    # Extract filenames after 'Successfully uploaded a group of 10 videos:' or 'photos:'
    success_files = re.findall(r'Successfully uploaded a group of \d+ (photos|videos):\s*(.*?)\s*(?=INFO|\Z)', content, re.DOTALL)

    # Print the extracted groups for debugging
    print("Extracted groups:", success_files)

    # Process each match and extract filenames (second item in the tuple)
    for group in success_files:
        file_list = group[1].split(', ')
        for filename in file_list:
            # Clean up filenames by removing newlines, timestamps, or anything after the file extension
            cleaned_filename = re.split(r'\s|\n', filename)[0]  # Split by space or newline, keep the first part
            filenames.append(cleaned_filename.strip())  # Strip any extra whitespace

# Remove duplicates and ensure filenames are trimmed properly
filenames = list(set(filenames))

# Print the final list of filenames for verification
print("Final list of filenames:", filenames)

# Copy each file from the source to the destination directory
for filename in filenames:
    if len(filename) > 0:
        print(f"Moving file {filename}")
        src_file = os.path.join(source_directory, filename)
        dest_file = os.path.join(destination_directory, filename)
        if os.path.exists(src_file):
            shutil.move(src_file, dest_file)
            print(f"Moved {filename} to {destination_directory}")
        else:
            print(f"File {filename} does not exist in {source_directory}")

print(f"All files processed. Total files moved: {len(filenames)}")
