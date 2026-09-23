import pytest
from sourcex.chunking import chunk_pages, split_into_chunks

def test_short_input():
    # A. Short input produces one chunk
    text = "This is a short text."
    chunks = split_into_chunks(text, chunk_size=50, chunk_overlap=10)
    assert len(chunks) == 1
    assert chunks[0] == text

def test_multiple_chunks_and_overlap():
    # B. Multiple chunks
    # C. Overlap verification
    # String of 10 characters: "0123456789"
    text = "0123456789"
    # chunk_size=4, overlap=2, step=2
    # Chunk 0: 0123
    # Chunk 1: 2345
    # Chunk 2: 4567
    # Chunk 3: 6789
    chunks = split_into_chunks(text, chunk_size=4, chunk_overlap=2)
    assert len(chunks) == 4
    assert chunks[0] == "0123"
    assert chunks[1] == "2345"
    assert chunks[2] == "4567"
    assert chunks[3] == "6789"
    # Verify overlap explicitly
    assert chunks[0][-2:] == chunks[1][:2]  # "23" == "23"

def test_exact_boundary_cases():
    # G. Exact boundary cases
    text = "0123456789"
    
    # Exact length = chunk size
    chunks = split_into_chunks(text, chunk_size=10, chunk_overlap=2)
    assert len(chunks) == 1
    
    # Chunk size slightly larger than text
    chunks = split_into_chunks(text, chunk_size=11, chunk_overlap=2)
    assert len(chunks) == 1
    
    # Chunk size leaves exactly 1 char for next chunk
    # step = 8 - 2 = 6
    # Chunk 0: 0-8 ("01234567")
    # Chunk 1: 6-14 ("6789") -> next step starts at 6
    chunks = split_into_chunks(text, chunk_size=8, chunk_overlap=2)
    assert len(chunks) == 2
    assert chunks[0] == "01234567"
    assert chunks[1] == "6789"

def test_empty_page():
    # F. Empty page
    pages = [{"document_id": "doc1", "filename": "f1.pdf", "page_number": 1, "text": "   "}]
    chunks = chunk_pages(pages)
    assert len(chunks) == 0

def test_page_attribution_and_metadata_preservation():
    # D. Page attribution
    # H. Metadata preservation
    pages = [{
        "document_id": "doc_abc",
        "filename": "test.pdf",
        "page_number": 5,
        "text": "12345"
    }]
    chunks = chunk_pages(pages, chunk_size=3, chunk_overlap=1)
    
    # step = 2. Chunks: "123", "345"
    assert len(chunks) == 2
    
    for i, c in enumerate(chunks):
        assert c.metadata.document_id == "doc_abc"
        assert c.metadata.source_file == "test.pdf"
        assert c.metadata.page_number == 5
        assert c.metadata.chunk_index == i

def test_multiple_pages():
    # E. Multiple pages
    pages = [
        {"document_id": "doc1", "filename": "test.pdf", "page_number": 1, "text": "page one"},
        {"document_id": "doc1", "filename": "test.pdf", "page_number": 2, "text": "page two content"}
    ]
    chunks = chunk_pages(pages, chunk_size=6, chunk_overlap=2)
    
    # page 1 chunks:
    # "page o", "e one"
    # page 2 chunks:
    # "page t", "e two ", "o cont", "ntent"
    
    assert len(chunks) == 6
    p1_chunks = [c for c in chunks if c.metadata.page_number == 1]
    p2_chunks = [c for c in chunks if c.metadata.page_number == 2]
    
    assert len(p1_chunks) == 2
    assert len(p2_chunks) == 4
    
    # Verify no accidental inheritance
    for c in p1_chunks:
        assert "one" in c.text or "page" in c.text or " e " in c.text
    for c in p2_chunks:
        assert "two" in c.text or "page" in c.text or "cont" in c.text or "tent" in c.text

def test_determinism():
    # I. Determinism
    text = "A consistent text that should chunk identically every time it is run."
    pages = [{"document_id": "1", "filename": "a.pdf", "page_number": 1, "text": text}]
    
    chunks_run1 = chunk_pages(pages, chunk_size=20, chunk_overlap=5)
    chunks_run2 = chunk_pages(pages, chunk_size=20, chunk_overlap=5)
    
    assert chunks_run1 == chunks_run2
