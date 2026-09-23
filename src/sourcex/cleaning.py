import re
from typing import List, Dict

def clean_text(text: str) -> str:
    """
    Applies conservative cleaning to extracted PDF text.
    - Strips leading/trailing whitespace from the entire document
    - Removes trailing line-level whitespace while preserving indentation
    - Normalizes excessive blank lines (3+ newlines become 2 newlines)
    """
    if not text:
        return ""
        
    # 1. Remove leading and trailing whitespace from the whole text
    text = text.strip()
    
    if not text:
        return ""
    
    # 2. Process line by line: remove trailing spaces but keep leading indentation 
    # (important for code blocks or bullet points)
    lines = text.split('\n')
    cleaned_lines = [line.rstrip() for line in lines]
    text = '\n'.join(cleaned_lines)
    
    # 3. Normalize excessive blank lines (reduce 3 or more consecutive newlines to exactly 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text

def clean_pages(pages: List[Dict]) -> List[Dict]:
    """
    Cleans the text content of a list of extracted pages while strictly preserving metadata
    and page boundaries.
    """
    cleaned_pages = []
    for page in pages:
        # Create a new dictionary to avoid mutating the original
        cleaned_page = {
            "document_id": page.get("document_id"),
            "filename": page.get("filename"),
            "page_number": page.get("page_number"),
            "text": clean_text(page.get("text", ""))
        }
        cleaned_pages.append(cleaned_page)
        
    return cleaned_pages
