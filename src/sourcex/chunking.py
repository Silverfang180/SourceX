from typing import List, Dict

# Practical baseline for MVP: character-based chunking.
# 1000 characters is roughly 200-300 tokens, which provides enough context 
# for a dense paragraph without diluting semantic meaning.
# 200 characters overlap ensures that sentences crossing chunk boundaries are not lost.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Splits a string into overlapping chunks based on character count.
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_len = len(text)
    
    # Calculate step size, ensuring we always move forward to avoid infinite loops
    step = max(1, chunk_size - chunk_overlap)
    
    while start < text_len:
        end = start + chunk_size
        chunks.append(text[start:end])
        
        if end >= text_len:
            break
            
        start += step
        
    return chunks

def chunk_pages(pages: List[Dict], chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[Dict]:
    """
    Takes a list of cleaned page dictionaries and returns a list of chunk dictionaries.
    Preserves document_id, filename, and page_number, and adds chunk_index.
    """
    chunks_output = []
    
    for page in pages:
        text = page.get("text", "")
        
        # Handle empty page text safely
        if not text.strip():
            continue
            
        page_chunks = split_into_chunks(text, chunk_size, chunk_overlap)
        
        for i, chunk_text in enumerate(page_chunks):
            chunk_record = {
                "document_id": page.get("document_id"),
                "filename": page.get("filename"),
                "page_number": page.get("page_number"),
                "chunk_index": i,
                "text": chunk_text
            }
            chunks_output.append(chunk_record)
            
    return chunks_output
