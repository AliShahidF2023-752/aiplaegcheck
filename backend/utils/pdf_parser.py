"""PDF text extraction utility."""
import io
from typing import BinaryIO

import pdfplumber


def extract_text_from_pdf(pdf_file: BinaryIO) -> str:
    """Extract text content from a PDF file.
    
    Args:
        pdf_file: Binary file object containing PDF data.
    
    Returns:
        Extracted text content from all pages.
    
    Raises:
        ValueError: If the PDF cannot be parsed or contains no text.
    """
    try:
        # Read the file content into bytes
        content = pdf_file.read()
        pdf_bytes = io.BytesIO(content)
        
        text_parts = []
        
        with pdfplumber.open(pdf_bytes) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        if not text_parts:
            raise ValueError("No text content found in PDF")
        
        return "\n\n".join(text_parts)
    
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")
