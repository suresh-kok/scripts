import os
import shutil
import logging
from datetime import datetime
import glob

def setup_logging(log_directory):
    """
    Sets up logging for the file-moving process.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    move_log_file = os.path.join(log_directory, f'move_log_{timestamp}.log')
    logging.basicConfig(
        filename=move_log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return move_log_file

def find_latest_log(log_directory, pattern):
    """
    Finds the latest log file matching the given pattern in the specified directory.
    """
    log_files = glob.glob(os.path.join(log_directory, pattern))
    if not log_files:
        return None
    # Sort log files by modification time, newest first
    log_files.sort(key=os.path.getmtime, reverse=True)
    return log_files[0]

def main():
    # === Configuration ===
    # Directory where the successful_uploads log files are stored
    log_directory = r'C:\Users\sures\OneDrive\Desktop\scripts\Telegram_Tools\Send_Messages'
    
    # Pattern to identify successful uploads log files
    successful_upload_log_pattern = 'successful_uploads_*.log'
    
    # Destination directory where files will be moved
    destination_directory = r'C:\Users\sures\Downloads\successful_upload'
    
    # === Setup ===
    # Ensure the destination directory exists
    os.makedirs(destination_directory, exist_ok=True)
    
    # Find the latest successful_uploads log file
    log_file_path = find_latest_log(log_directory, successful_upload_log_pattern)
    if not log_file_path:
        print("No successful upload log files found.")
        return
    
    print(f"Using log file: {log_file_path}")
    
    # Setup logging for the moving process
    move_log_file = setup_logging(log_directory)
    logging.info(f"Starting file move process using log file: {log_file_path}")
    
    # === Extract File Paths ===
    file_paths = []
    try:
        with open(log_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    # Split the line at the first ' - ' to separate timestamp from the file path
                    parts = line.split(' - ', 1)
                    if len(parts) == 2:
                        file_path = parts[1]
                        file_paths.append(file_path)
                    else:
                        logging.warning(f"Unrecognized log format: {line}")
                        print(f"Unrecognized log format: {line}")
    except Exception as e:
        logging.error(f"Failed to read log file {log_file_path}. Error: {str(e)}")
        print(f"Failed to read log file: {str(e)}")
        return
    
    # Remove duplicates
    file_paths = list(set(file_paths))
    
    print(f"Total files to move: {len(file_paths)}")
    
    # === Move Files ===
    moved_count = 0
    failed_count = 0  # Initialize failed count
    
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        dest_file = os.path.join(destination_directory, filename)
        
        if os.path.exists(file_path):
            try:
                shutil.move(file_path, dest_file)
                logging.info(f"Moved {file_path} to {dest_file}")
                print(f"Moved: {filename}")
                moved_count += 1
            except Exception as e:
                logging.error(f"Failed to move {file_path} to {dest_file}. Error: {str(e)}")
                print(f"Failed to move {filename}: {str(e)}")
                failed_count += 1  # Increment failed count
        else:
            logging.warning(f"File does not exist: {file_path}")
            print(f"File does not exist: {filename}")
            # Optionally, you can decide whether missing files count as failures
            # failed_count += 1  # Uncomment if you want to count missing files as failures
    
    # === Summary ===
    logging.info(f"File move process completed. Total files moved: {moved_count}, Total files failed to move: {failed_count}")
    print(f"All files processed. Total files moved: {moved_count}")
    print(f"Total files failed to move: {failed_count}")  # Print failed count

if __name__ == '__main__':
    main()
