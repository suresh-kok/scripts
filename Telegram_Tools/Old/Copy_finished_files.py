import os
import shutil
import re

# Define the source and destination directories
source_directory = 'C:\\Users\\sures\\Downloads\\pictures\\less_than_1MB'
destination_directory = 'C:\\Users\\sures\\Downloads\\successful_upload'

# Ensure the destination directory exists
os.makedirs(destination_directory, exist_ok=True)

# Define the log file path
log_file_path = r'C:\Users\sures\OneDrive\Desktop\scripts\Telegram_Tools\Send_Messages\upload_log_20240912_205332.log'

# Read the log file and extract filenames
filenames = []
with open(log_file_path, 'r') as file:
    content = file.read()
    
    # Regular expression to extract filenames after "Successfully uploaded a group of" (handles line breaks)
    success_files = re.findall(r'Successfully uploaded a group of \d+ (photos|videos):\s*(.*?)(?=INFO|\Z)', content, re.DOTALL)
    
    for _, group in success_files:
        # Split filenames by commas, strip extra spaces, and append to the list
        filenames.extend([filename.strip() for filename in group.split(', ')])
    
# Remove duplicates and empty entries
filenames = list(set([filename for filename in filenames if filename]))

print("Filenames to move: %s" % filenames)

# Copy each file from the source to the destination directory
for filename in filenames:
    src_file = os.path.join(source_directory, filename)
    dest_file = os.path.join(destination_directory, filename)
    
    if os.path.exists(src_file):
        shutil.move(src_file, dest_file)
        print(f"Moved {filename} to {destination_directory}")
    else:
        print(f"File {filename} does not exist in {source_directory}")

print(f"All files processed. Total files moved: {len(filenames)}")
