"""
Logger configuration module for the AutoML pipeline.
"""

import sys
import os
import logging
from datetime import datetime, timezone, timedelta

os.makedirs("logs", exist_ok=True)
kst = timezone(timedelta(hours=9))
timestamp = datetime.now(kst).strftime("%Y%m%d_%H%M%S")
LOG_FILE = f"logs/process_{timestamp}.log"

logger = logging.getLogger("automl_logger")
logger.setLevel(logging.INFO)
logger.propagate = False

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


class TeeLogger:
    """
    Redirects sys.stdout and sys.stderr to both the terminal and a log file.
    """

    def __init__(self, filename):
        """
        Initialize the TeeLogger.

        Parameters
            filename : str
                Path to the log file.
        """
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        """
        Write a message to both the terminal and the log file.

        Parameters
            message : str
                The message to write.
        """
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        """
        Flush the streams for both the terminal and the log file.
        """
        self.terminal.flush()
        self.log.flush()


tee = TeeLogger(LOG_FILE)
sys.stdout = tee
sys.stderr = tee