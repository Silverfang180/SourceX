import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from sourcex.config import config
from sourcex.metadata import Chunk, ChunkMetadata
from sourcex.retrieval.embeddings import EmbeddedChunk, EmbeddingError
from sourcex.retrieval.index import VectorStore, SearchResult
from sourcex.retrieval.retriever import Retriever

def create_synthetic_chunk(idx: int, dim: int = 768) -> EmbeddedChunk:
    meta = ChunkMetadata(
        document_id=f"doc_{idx}",
        source_file=f"file_{idx}.pdf",
        page_number=idx,
        chunk_index=0
    )
    chunk = Chunk(text=f"This is chunk {idx}", metadata=meta)
    
    vector = np.zeros(dim, dtype=np.float32)
    if idx < dim:
        vector[idx] = 1.0
        
    return EmbeddedChunk(chunk=chunk, embedding=vector.tolist())

@pytest.fixture
def populated_vector_store():
    store = VectorStore(dimension=768)
    chunks = [create_synthetic_chunk(i) for i in range(5)]
    store.add_chunks(chunks)
    return store

@patch("sourcex.retrieval.retriever.embed_query")
def test_retriever_search_success(mock_embed_query, populated_vector_store):
    retriever = Retriever(populated_vector_store)
    
    # Mock embed_query to return a vector matching chunk 2
    query_vector = np.zeros(768, dtype=np.float32)
    query_vector[2] = 1.0
    mock_embed_query.return_value = query_vector.tolist()
    
    results = retriever.search("Find chunk 2", k=3)
    
    mock_embed_query.assert_called_once_with("Find chunk 2")
    
    assert len(results) == 3
    assert isinstance(results[0], SearchResult)
    assert results[0].chunk.text == "This is chunk 2"
    assert results[0].score == 1.0
    
    # Validate metadata preservation
    assert results[0].chunk.metadata.document_id == "doc_2"
    assert results[0].chunk.metadata.source_file == "file_2.pdf"

@patch("sourcex.retrieval.retriever.embed_query")
def test_retriever_search_k_behavior(mock_embed_query, populated_vector_store):
    retriever = Retriever(populated_vector_store)
    mock_embed_query.return_value = np.zeros(768, dtype=np.float32).tolist()
    
    # Request more results than exist
    results = retriever.search("query", k=10)
    assert len(results) == 5
    
    # Request exactly 1
    results = retriever.search("query", k=1)
    assert len(results) == 1
    
    # Request 0 or less
    assert retriever.search("query", k=0) == []
    assert retriever.search("query", k=-5) == []

def test_retriever_empty_query(populated_vector_store):
    retriever = Retriever(populated_vector_store)
    
    with pytest.raises(ValueError, match="Query cannot be empty."):
        retriever.search("")
        
    with pytest.raises(ValueError, match="Query cannot be empty."):
        retriever.search("   ")

@patch("sourcex.retrieval.retriever.embed_query")
def test_retriever_embedding_failure(mock_embed_query, populated_vector_store):
    retriever = Retriever(populated_vector_store)
    
    # Simulate API failure propagating from embed_query
    mock_embed_query.side_effect = EmbeddingError("API down")
    
    with pytest.raises(EmbeddingError, match="API down"):
        retriever.search("test")
