import logging
import sys
from pathlib import Path

# Create logs directory
Path("logs").mkdir(exist_ok=True)


def setup_logger(name: str = "recruitment_app", level: int = logging.INFO):
    """Setup logger with file and console handlers with UTF-8 encoding support"""
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler("logs/app.log", encoding='utf-8')
    file_handler.setLevel(level)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_format)
    
    # Console handler with UTF-8 encoding support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    
    # Set UTF-8 encoding for stdout on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass  # Ignore if reconfiguration fails
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

