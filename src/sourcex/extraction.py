import os
import fitz  # PyMuPDF
import hashlib
from typing import List, Dict, Optional

def extract_pdf(file_path: str, document_id: Optional[str] = None) -> List[Dict]:
    """
    Extracts text from a PDF file page by page.
    
    Args:
        file_path: Path to the PDF file.
        document_id: Optional unique identifier for the document. If None, it will be generated from filename.
        
    Returns:
        A list of dictionaries, where each dictionary represents a page with text and metadata.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
        
    if not file_path.lower().endswith('.pdf'):
        raise ValueError(f"File is not a PDF: {file_path}")
        
    filename = os.path.basename(file_path)
    
    if document_id is None:
        # Generate a basic ID if not provided
        document_id = hashlib.md5(filename.encode()).hexdigest()
        
    extracted_pages = []
    
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise ValueError(f"Failed to open PDF file {file_path}: {e}")
        
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        
        # Basic text cleanup (minimal, T003 handles advanced cleaning)
        # Stripping leading/trailing whitespace prevents blank pages from being full of newlines
        text = text.strip() if text else ""
        
        extracted_pages.append({
            "document_id": document_id,
            "filename": filename,
            "page_number": page_num + 1,  # 1-indexed for human readability
            "text": text
        })
        
    doc.close()
    return extracted_pages
