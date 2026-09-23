import pytest
from unittest.mock import patch, MagicMock

from sourcex.metadata import Chunk, ChunkMetadata
from sourcex.retrieval.embeddings import embed_texts, embed_chunks, EmbeddedChunk, EmbeddingError
from sourcex.config import config
from google.genai.errors import APIError

@pytest.fixture
def sample_chunks():
    meta1 = ChunkMetadata("doc1", "f1.pdf", 1, 0)
    meta2 = ChunkMetadata("doc1", "f1.pdf", 1, 1)
    return [
        Chunk(text="first chunk", metadata=meta1),
        Chunk(text="second chunk", metadata=meta2)
    ]

@patch("sourcex.retrieval.embeddings.get_embedding_client")
def test_embed_chunks_success(mock_get_client, sample_chunks):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_response = MagicMock()
    emb1 = MagicMock()
    emb1.values = [0.1] * config.EMBEDDING_DIMENSIONS
    emb2 = MagicMock()
    emb2.values = [0.2] * config.EMBEDDING_DIMENSIONS
    
    mock_response.embeddings = [emb1, emb2]
    mock_client.models.embed_content.return_value = mock_response
    
    embedded = embed_chunks(sample_chunks)
    
    # Verify mock call arguments to ensure correct gemini-embedding-2 API contract
    mock_client.models.embed_content.assert_called_once()
    call_kwargs = mock_client.models.embed_content.call_args.kwargs
    assert call_kwargs["model"] == config.EMBEDDING_MODEL
    assert call_kwargs["contents"] == ["title: none | text: first chunk", "title: none | text: second chunk"]
    
    # Ensure config only has dimensionality, not task_type
    embed_config = call_kwargs["config"]
    assert embed_config.output_dimensionality == config.EMBEDDING_DIMENSIONS
    assert not hasattr(embed_config, "task_type") or embed_config.task_type is None
    
    assert len(embedded) == 2
    assert isinstance(embedded[0], EmbeddedChunk)
    assert embedded[0].chunk.text == "first chunk"
    assert embedded[0].embedding == [0.1] * config.EMBEDDING_DIMENSIONS
    assert embedded[1].chunk.text == "second chunk"
    assert embedded[1].embedding == [0.2] * config.EMBEDDING_DIMENSIONS
    
    # Input order preserved, metadata unchanged
    assert embedded[0].chunk.metadata.chunk_index == 0
    assert embedded[1].chunk.metadata.chunk_index == 1

@patch("sourcex.retrieval.embeddings.get_embedding_client")
def test_embed_texts_api_failure(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    # Simulate a 429 APIError
    mock_client.models.embed_content.side_effect = APIError("429 Too Many Requests", 429)
    
    with pytest.raises(EmbeddingError, match="Gemini API Error: 429 Too Many Requests"):
        embed_texts(["some text"])

@patch("sourcex.retrieval.embeddings.get_embedding_client")
def test_embed_texts_malformed_response(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    # Return 1 embedding instead of 2
    mock_response = MagicMock()
    emb1 = MagicMock()
    emb1.values = [0.1] * config.EMBEDDING_DIMENSIONS
    mock_response.embeddings = [emb1]
    
    mock_client.models.embed_content.return_value = mock_response
    
    with pytest.raises(EmbeddingError, match="Expected 2 embeddings, got 1"):
        embed_texts(["text1", "text2"])

@patch("sourcex.retrieval.embeddings.get_embedding_client")
def test_embed_texts_invalid_dimensionality(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    # Return wrong dimensionality
    mock_response = MagicMock()
    emb1 = MagicMock()
    emb1.values = [0.1] * 50 # Not 768
    mock_response.embeddings = [emb1]
    
    mock_client.models.embed_content.return_value = mock_response
    
    with pytest.raises(EmbeddingError, match=f"Expected dimensionality {config.EMBEDDING_DIMENSIONS}, got 50"):
        embed_texts(["text1"])

def test_embed_texts_empty_input():
    # Should not call the API or crash
    assert embed_texts([]) == []
    assert embed_chunks([]) == []
