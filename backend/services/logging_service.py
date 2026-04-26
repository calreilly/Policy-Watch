import logging
import os
from datetime import datetime

# Path to the persistent error log
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "app_errors.log")

# Configure logger
logger = logging.getLogger("PolicyWatchLoader")
logger.setLevel(logging.ERROR)

# File Handlers
file_handler = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def log_error(error_msg: str, context: str = "General"):
    """Registers a persistent error entry for debugging after platform testing."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{context}] {error_msg}"
    logger.error(formatted_msg)
    print(f"FAILED INTELLIGENCE LOGGED: {formatted_msg}")

def get_recent_errors(limit: int = 50):
    """Utility to retrieve logged errors from disk for presentation audit."""
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r") as f:
            return f.readlines()[-limit:]
    except:
        return []
