import os
import re
import shutil

def copy_and_rename_files(directory):
    # Regular expression to match the season and episode numbers
    pattern = re.compile(r'Season (\d+) Episode (\d+)')
    
    for filename in os.listdir(directory):
        match = pattern.search(filename)
        if match:
            season = match.group(1)
            episode = match.group(2)
            new_folder = os.path.join(directory, f"Season {season}")
            new_name = f"Episode {episode}.mp4"
            
            # Create the new folder if it doesn't exist
            os.makedirs(new_folder, exist_ok=True)
            
            # Construct full file paths
            old_file_path = os.path.join(directory, filename)
            new_file_path = os.path.join(new_folder, new_name)
            
            # Print the old and new names
            print(f"Old Name: {old_file_path}")
            print(f"New Name: {new_file_path}")
            print()
            
            # Copy the file to the new location
            shutil.copy(old_file_path, new_file_path)

# Specify the directory containing the files
directory = 'C:\\Users\\sures\\Downloads\\The Big Bang Theory'

# Call the function
copy_and_rename_files(directory)
