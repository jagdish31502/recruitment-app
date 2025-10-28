"""
File handling utilities for document processing
"""
import os
import tempfile
from pathlib import Path
from typing import BinaryIO, Optional

logger = __import__("logging").getLogger(__name__)


def save_uploaded_file(uploaded_file: BinaryIO, filename: str) -> str:
    """Save uploaded file to temporary directory"""
    temp_dir = Path(tempfile.gettempdir()) / "recruitment_uploads"
    temp_dir.mkdir(exist_ok=True)
    
    file_path = temp_dir / filename
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    
    return str(file_path)


def delete_file(file_path: str) -> bool:
    """Delete a file safely"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename"""
    return Path(filename).suffix.lower()


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """Validate if file extension is allowed"""
    ext = get_file_extension(filename)
    return ext in allowed_extensions

