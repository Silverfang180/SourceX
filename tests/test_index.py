import pytest
import os
import shutil
import numpy as np

from sourcex.metadata import Chunk, ChunkMetadata
from sourcex.retrieval.embeddings import EmbeddedChunk
from sourcex.retrieval.index import VectorStore, IndexDimensionError, SearchResult

@pytest.fixture
def temp_dir(tmp_path):
    d = tmp_path / "faiss_test"
    d.mkdir()
    yield str(d)
    if d.exists():
        shutil.rmtree(d)

def create_synthetic_chunk(idx: int, dim: int = 768) -> EmbeddedChunk:
    meta = ChunkMetadata(
        document_id=f"doc_{idx}",
        source_file=f"file_{idx}.pdf",
        page_number=idx,
        chunk_index=0
    )
    chunk = Chunk(text=f"This is chunk {idx}", metadata=meta)
    
    # Create a vector that will have a predictable inner product
    # e.g., one-hot vectors, or just random
    # Here we'll make simple one-hot-like vectors for easy distance predicting
    vector = np.zeros(dim, dtype=np.float32)
    if idx < dim:
        vector[idx] = 1.0
    
    return EmbeddedChunk(chunk=chunk, embedding=vector.tolist())

def test_initialization():
    store = VectorStore(dimension=768)
    assert store.dimension == 768
    assert store.index.ntotal == 0
    assert len(store.chunk_mapping) == 0

def test_add_vectors_and_metadata_mapping():
    store = VectorStore(dimension=768)
    ec1 = create_synthetic_chunk(0)
    ec2 = create_synthetic_chunk(1)
    
    store.add_chunks([ec1, ec2])
    
    assert store.index.ntotal == 2
    assert len(store.chunk_mapping) == 2
    assert store.next_id == 2
    
    # Verify metadata mapping
    assert store.chunk_mapping[0].text == "This is chunk 0"
    assert store.chunk_mapping[1].text == "This is chunk 1"
    assert store.chunk_mapping[0].metadata.document_id == "doc_0"
    assert store.chunk_mapping[1].metadata.source_file == "file_1.pdf"

def test_wrong_dimensions_add():
    store = VectorStore(dimension=768)
    bad_chunk = create_synthetic_chunk(0, dim=50) # Wrong dimension
    
    with pytest.raises(IndexDimensionError, match="Expected dimension 768"):
        store.add_chunks([bad_chunk])

def test_search_ranking():
    store = VectorStore(dimension=768)
    chunks = [create_synthetic_chunk(i) for i in range(5)]
    store.add_chunks(chunks)
    
    # Query vector matching chunk 2 exactly (one-hot at index 2)
    query = np.zeros(768, dtype=np.float32)
    query[2] = 1.0
    query_list = query.tolist()
    
    results = store.search(query_list, k=3)
    
    assert len(results) == 3
    assert isinstance(results[0], SearchResult)
    
    # The nearest neighbor should be chunk 2, score 1.0 (inner product of identical one-hot)
    assert results[0].chunk.text == "This is chunk 2"
    assert results[0].score == 1.0
    assert results[0].chunk.metadata.page_number == 2

def test_empty_index_search():
    store = VectorStore(dimension=768)
    query = np.zeros(768, dtype=np.float32).tolist()
    
    results = store.search(query, k=5)
    assert results == []

def test_k_larger_than_index_size():
    store = VectorStore(dimension=768)
    store.add_chunks([create_synthetic_chunk(0), create_synthetic_chunk(1)])
    
    query = np.zeros(768, dtype=np.float32).tolist()
    results = store.search(query, k=10)
    
    assert len(results) == 2

def test_invalid_query_dimension():
    store = VectorStore(dimension=768)
    store.add_chunks([create_synthetic_chunk(0)])
    
    bad_query = np.zeros(50, dtype=np.float32).tolist()
    
    with pytest.raises(IndexDimensionError, match="Expected query dimension 768"):
        store.search(bad_query, k=5)

def test_save_load_round_trip(temp_dir):
    store1 = VectorStore(dimension=768)
    chunks = [create_synthetic_chunk(i) for i in range(3)]
    store1.add_chunks(chunks)
    
    query = np.zeros(768, dtype=np.float32)
    query[1] = 1.0
    query_list = query.tolist()
    
    # Search before save
    results1 = store1.search(query_list, k=1)
    assert results1[0].chunk.text == "This is chunk 1"
    
    # Save
    store1.save(temp_dir)
    
    # Load into a new store
    store2 = VectorStore(dimension=768)
    store2.load(temp_dir)
    
    assert store2.index.ntotal == 3
    assert len(store2.chunk_mapping) == 3
    assert store2.next_id == 3
    
    # Search after load
    results2 = store2.search(query_list, k=1)
    
    # Verify vector count, ranking, scores, and metadata preserved
    assert len(results2) == 1
    assert results2[0].chunk.text == "This is chunk 1"
    assert abs(results2[0].score - results1[0].score) < 1e-6
    assert results2[0].chunk.metadata.document_id == "doc_1"

def test_id_uniqueness_multiple_adds():
    store = VectorStore(dimension=768)
    store.add_chunks([create_synthetic_chunk(0), create_synthetic_chunk(1)])
    store.add_chunks([create_synthetic_chunk(2)])
    
    assert store.index.ntotal == 3
    assert len(store.chunk_mapping) == 3
    
    # Verify IDs are 0, 1, 2
    assert set(store.chunk_mapping.keys()) == {0, 1, 2}
    
    assert store.chunk_mapping[0].metadata.document_id == "doc_0"
    assert store.chunk_mapping[1].metadata.document_id == "doc_1"
    assert store.chunk_mapping[2].metadata.document_id == "doc_2"
