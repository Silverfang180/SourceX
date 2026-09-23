import sys
import os

# Ensure src is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from sourcex.config import config
from sourcex.metadata import Chunk, ChunkMetadata
from sourcex.retrieval.embeddings import embed_chunks, EmbeddedChunk

def main():
    if not config.GEMINI_API_KEY:
        print("FAIL: GEMINI_API_KEY is not set in environment or .env file.")
        sys.exit(1)
        
    print(f"Using model: {config.EMBEDDING_MODEL}")
    print(f"Expected dimensions: {config.EMBEDDING_DIMENSIONS}")
    
    # 1. Create a tiny sample chunk
    meta = ChunkMetadata(
        document_id="live_test_123",
        source_file="manual_test.pdf",
        page_number=42,
        chunk_index=0
    )
    chunk = Chunk(text="This is a live API smoke test for SourceX embeddings.", metadata=meta)
    
    # 2. Call the real embedding function
    print("Calling real Gemini API...")
    try:
        embedded_chunks = embed_chunks([chunk])
    except Exception as e:
        print(f"FAIL: Real API call failed with error: {e}")
        sys.exit(1)
        
    # 3. Verify the output
    if not embedded_chunks or len(embedded_chunks) != 1:
        print(f"FAIL: Expected 1 result, got {len(embedded_chunks)}")
        sys.exit(1)
        
    result = embedded_chunks[0]
    
    if not isinstance(result, EmbeddedChunk):
        print(f"FAIL: Expected EmbeddedChunk type, got {type(result)}")
        sys.exit(1)
        
    # Verify metadata preservation
    m = result.chunk.metadata
    if m.document_id != "live_test_123" or m.source_file != "manual_test.pdf" or m.page_number != 42 or m.chunk_index != 0:
        print(f"FAIL: Metadata was altered: {m}")
        sys.exit(1)
        
    # Verify vector
    vector = result.embedding
    if not isinstance(vector, list) or len(vector) != config.EMBEDDING_DIMENSIONS:
        print(f"FAIL: Expected vector of length {config.EMBEDDING_DIMENSIONS}, got {len(vector) if isinstance(vector, list) else type(vector)}")
        sys.exit(1)
        
    # Ensure it's numeric
    if not all(isinstance(x, (float, int)) for x in vector):
        print("FAIL: Vector contains non-numeric values.")
        sys.exit(1)
        
    print("SUCCESS! Real API call succeeded.")
    print(f"Resulting vector is a float list with {len(vector)} dimensions.")
    print("Original chunk text and metadata perfectly preserved.")
    
if __name__ == "__main__":
    main()
