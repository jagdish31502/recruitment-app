"""
Document processor for extracting text from various file formats
"""
from .pdf_extractor import extract_text_from_pdf
from .docx_extractor import extract_text_from_docx


def extract_text_from_file(file_path: str, file_extension: str) -> str:
    """Extract text from file based on extension"""
    extension_lower = file_extension.lower()
    
    if extension_lower == '.pdf':
        return extract_text_from_pdf(file_path)
    elif extension_lower in ['.doc', '.docx']:
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

