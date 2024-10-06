import os
from PIL import Image
import shutil  # Import shutil for moving files

# Set the directory you want to clean up
directory = 'C:\\Users\\sures\\Downloads\\pictures\\less_than_1MB'

# Set the destination directory for moved files
destination = 'C:\\Users\\sures\\Downloads\\pictures\\moved_files'

# Ensure the destination directory exists
if not os.path.exists(destination):
    os.makedirs(destination)

# Loop through each file in the directory
for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    move_file = False

    if filename.endswith("thumb.jpg"):  # Check if the file ends with 'thumb'
        move_file = True
    else:
        try:
            # Open the image to check its resolution
            with Image.open(file_path) as img:
                width, height = img.size

            # Check if both dimensions are less than 1000px
            if width < 1000 and height < 1000:
                move_file = True

        except IOError:
            # This handles the case where the file isn't an image or can't be opened
            print(f"Cannot open or it's not an image {file_path}.")
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

    if move_file:
        try:
            dest_file_path = os.path.join(destination, filename)
            shutil.move(file_path, dest_file_path)  # Move the file
            print(f"Moved {file_path} to {dest_file_path}")
        except Exception as e:
            print(f"Failed to move {file_path}: {str(e)}")
