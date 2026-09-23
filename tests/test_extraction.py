import os
import pytest
import fitz
from sourcex.extraction import extract_pdf

@pytest.fixture
def sample_pdf(tmp_path):
    """Creates a sample PDF for testing using PyMuPDF"""
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    
    # Page 1 - Standard text
    page1 = doc.new_page()
    page1.insert_text((50, 50), "This is page 1.")
    
    # Page 2 - Empty page
    doc.new_page()
    
    # Page 3 - Standard text
    page3 = doc.new_page()
    page3.insert_text((50, 50), "This is page 3.")
    
    doc.save(str(pdf_path))
    doc.close()
    
    return str(pdf_path)

def test_extract_pdf_valid(sample_pdf):
    pages = extract_pdf(sample_pdf, document_id="doc-123")
    
    assert len(pages) == 3
    
    # Check page 1
    assert pages[0]["document_id"] == "doc-123"
    assert pages[0]["filename"] == "sample.pdf"
    assert pages[0]["page_number"] == 1
    assert "This is page 1." in pages[0]["text"]
    
    # Check page 2 (Empty)
    assert pages[1]["page_number"] == 2
    assert pages[1]["text"] == ""
    
    # Check page 3
    assert pages[2]["page_number"] == 3
    assert "This is page 3." in pages[2]["text"]

def test_extract_pdf_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_pdf("nonexistent.pdf")

def test_extract_pdf_invalid_extension(tmp_path):
    txt_path = tmp_path / "not_a_pdf.txt"
    txt_path.write_text("hello")
    with pytest.raises(ValueError, match="not a PDF"):
        extract_pdf(str(txt_path))

def test_extract_pdf_invalid_pdf_content(tmp_path):
    bad_pdf = tmp_path / "bad.pdf"
    bad_pdf.write_text("This is not a real PDF format")
    with pytest.raises(ValueError, match="Failed to open PDF file"):
        extract_pdf(str(bad_pdf))

def test_extract_pdf_auto_document_id(sample_pdf):
    pages = extract_pdf(sample_pdf)
    assert len(pages) > 0
    assert pages[0]["document_id"] is not None
    assert isinstance(pages[0]["document_id"], str)
    assert len(pages[0]["document_id"]) > 0
