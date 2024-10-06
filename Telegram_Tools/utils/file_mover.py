# utils/file_mover.py

import os
import shutil
import glob
import logging

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

def extract_file_paths_from_log(log_file_path):
    """
    Extracts file paths from a log file.
    Assumes each line in the log file is in the format: 'timestamp - file_path'
    """
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
    return file_paths

def move_files(file_paths, destination_directory):
    """
    Moves files to the destination directory, handling duplicates by appending a counter.
    Returns the counts of moved and failed files.
    """
    os.makedirs(destination_directory, exist_ok=True)
    moved_count = 0
    failed_count = 0

    # Remove duplicates
    unique_file_paths = list(set(file_paths))
    
    logging.info(f"Total unique files to move: {len(unique_file_paths)}")
    print(f"Total unique files to move: {len(unique_file_paths)}")
    
    for file_path in unique_file_paths:
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
                failed_count += 1
        else:
            logging.warning(f"File does not exist: {file_path}")
            print(f"File does not exist: {filename}")
            # Optionally, decide whether missing files count as failures
            # failed_count += 1

    return moved_count, failed_count
