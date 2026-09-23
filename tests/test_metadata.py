from sourcex.metadata import Chunk, ChunkMetadata

def test_metadata_instantiation():
    """Verify that the metadata schema can be populated correctly."""
    meta = ChunkMetadata(
        document_id="doc_123",
        source_file="test.pdf",
        page_number=1,
        chunk_index=0
    )
    
    assert meta.document_id == "doc_123"
    assert meta.source_file == "test.pdf"
    assert meta.page_number == 1
    assert meta.chunk_index == 0

def test_chunk_instantiation():
    """Verify that a Chunk holds text and metadata properly."""
    meta = ChunkMetadata(
        document_id="doc_123",
        source_file="test.pdf",
        page_number=1,
        chunk_index=0
    )
    
    chunk = Chunk(text="Sample text", metadata=meta)
    
    assert chunk.text == "Sample text"
    assert chunk.metadata.document_id == "doc_123"
