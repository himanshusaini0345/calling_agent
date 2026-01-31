# app/core/logging_config.py

import logging
import colorlog
import os
from datetime import datetime

# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_FILENAME = "\033[36m"     # Cyan
COLOR_FUNCNAME = "\033[35m"     # Magenta
COLOR_LINENO = "\033[33m"       # Yellow
COLOR_MESSAGE = "\033[93m"      # White (bright)

class LineRotatingFileHandler(logging.FileHandler):
    """
    Custom log handler that rotates logs based on number of lines.
    """
    def __init__(self, filename, max_lines=10000, encoding=None):
        self.base_filename = filename
        self.max_lines = max_lines
        self.current_lines = 0

        # Count existing lines if file exists
        if os.path.exists(filename):
            with open(filename, "r", encoding=encoding or "utf-8", errors="ignore") as f:
                self.current_lines = sum(1 for _ in f)

        super().__init__(filename, mode="a", encoding=encoding)

    def emit(self, record):
        # Rotate if too many lines
        if self.current_lines >= self.max_lines:
            self.rotate_file()

        super().emit(record)
        self.current_lines += 1

    def rotate_file(self):
        """Rename the current log file with timestamp."""
        self.close()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated_name = f"{self.base_filename.rstrip('.log')}_{timestamp}.log"
        os.rename(self.base_filename, rotated_name)
        # Start a new file
        self.stream = open(self.base_filename, "w", encoding=self.encoding)
        self.current_lines = 0

def setup_logging():
    """Configures the application's logger."""
    logger = logging.getLogger("app") # Use a named logger
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    log_colors = {
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
    log_format = (
        '%(asctime)s | '
        '%(log_color)s%(levelname)-8s%(reset)s | '
        '%(name)s:' +
        COLOR_FILENAME + '%(filename)s' + COLOR_RESET + ':' +
        COLOR_FUNCNAME + '%(funcName)s' + COLOR_RESET + ':' +
        COLOR_LINENO + '%(lineno)d' + COLOR_RESET + ' - ' +
        COLOR_MESSAGE + '%(message)s' + COLOR_RESET
    )
    console_formatter = colorlog.ColoredFormatter(
        log_format,
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors=log_colors
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # ---- File Handler (Plain Text + Auto Rotation by Lines) ----
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    file_handler = LineRotatingFileHandler(log_file, max_lines=5000, encoding="utf-8")
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(filename)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    logger.info("Logging setup complete. Logs will rotate after 5000 lines.")
# Get the root logger for app components
# This allows other modules to just call logging.getLogger(__name__)
# and inherit the configuration.
logger = logging.getLogger("app")