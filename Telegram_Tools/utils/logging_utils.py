# utils/logging_utils.py

import os
import logging
from datetime import datetime

def setup_logging(log_directory):
    """
    Sets up logging for the entire application with UTF-8 encoding.
    """
    os.makedirs(log_directory, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_directory, f'process_log_{timestamp}.log')
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )
    
    # Also set up console logging
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    logging.info("Logging is set up.")
    return log_file
