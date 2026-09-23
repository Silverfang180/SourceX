from sourcex.cleaning import clean_text, clean_pages

def test_leading_trailing_whitespace():
    """Test 1: Strip outer whitespace"""
    assert clean_text("   Hello World   ") == "Hello World"
    assert clean_text("\n\nHello World\n\n") == "Hello World"

def test_repeated_blank_lines():
    """Test 2: Normalize excessive blank lines"""
    text = "Hello\n\n\n\nWorld\n\n\nTest"
    cleaned = clean_text(text)
    assert cleaned == "Hello\n\nWorld\n\nTest"

def test_metadata_and_multiple_pages():
    """Test 3, 4, 5: Verify metadata preservation, page independence, and separation"""
    pages = [
        {"document_id": "doc1", "filename": "f1.pdf", "page_number": 1, "text": "  Page 1 text  \n\n\n"},
        {"document_id": "doc1", "filename": "f1.pdf", "page_number": 2, "text": "\nPage 2 text"}
    ]
    cleaned = clean_pages(pages)
    
    assert len(cleaned) == 2
    # Check page 1
    assert cleaned[0]["document_id"] == "doc1"
    assert cleaned[0]["filename"] == "f1.pdf"
    assert cleaned[0]["page_number"] == 1
    assert cleaned[0]["text"] == "Page 1 text"
    
    # Check page 2
    assert cleaned[1]["document_id"] == "doc1"
    assert cleaned[1]["filename"] == "f1.pdf"
    assert cleaned[1]["page_number"] == 2
    assert cleaned[1]["text"] == "Page 2 text"

def test_meaning_preservation():
    """Test 6: Verify meaning, punctuation, numbers, and indentation are preserved"""
    text = (
        "def hello_world():\n"
        "    print(\"Hello, world!\")\n"
        "\n"
        "1. First point\n"
        "2. Second point"
    )
    cleaned = clean_text(text)
    assert "def hello_world():" in cleaned
    assert 'print("Hello, world!")' in cleaned
    assert "1. First point" in cleaned
    assert "    print" in cleaned  # Indentation preserved

def test_empty_page():
    """Test 7: Verify empty pages do not crash"""
    assert clean_text("") == ""
    assert clean_text("   \n   \n") == ""
    
    pages = [{"document_id": "1", "filename": "1.pdf", "page_number": 1, "text": "   "}]
    cleaned = clean_pages(pages)
    assert cleaned[0]["text"] == ""

def test_idempotence():
    """Test 8: Verify cleaning clean text doesn't change it"""
    text = "Hello\n\nWorld"
    assert clean_text(text) == clean_text(clean_text(text))
