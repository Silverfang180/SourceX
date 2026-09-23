import pytest
from unittest.mock import patch, MagicMock
from google.genai.errors import APIError

from sourcex.metadata import Chunk, ChunkMetadata
from sourcex.retrieval.index import SearchResult
from sourcex.generation.rag import (
    generate_answer,
    build_prompt,
    GenerationError,
    GenerationResult,
)
from sourcex.config import config

@pytest.fixture
def sample_results():
    meta1 = ChunkMetadata(source_file="test1.pdf", page_number=1, chunk_index=0, document_id="doc1")
    chunk1 = Chunk(text="Paris is the capital of France.", metadata=meta1)
    res1 = SearchResult(chunk=chunk1, score=0.9)
    
    meta2 = ChunkMetadata(source_file="test2.pdf", page_number=2, chunk_index=1, document_id="doc2")
    chunk2 = Chunk(text="The Eiffel Tower is in Paris.", metadata=meta2)
    res2 = SearchResult(chunk=chunk2, score=0.8)
    
    return [res1, res2]

def test_build_prompt(sample_results):
    query = "Where is the Eiffel Tower?"
    prompt = build_prompt(query, sample_results)
    
    assert "Where is the Eiffel Tower?" in prompt
    assert "Paris is the capital of France." in prompt
    assert "[Document 1]" in prompt
    assert "[Document 2]" in prompt
    assert "The Eiffel Tower is in Paris." in prompt

def test_build_prompt_empty_results():
    query = "Where is the Eiffel Tower?"
    prompt = build_prompt(query, [])
    
    assert "Where is the Eiffel Tower?" in prompt
    assert "No relevant context found." in prompt

@patch("sourcex.generation.rag.get_generation_client")
def test_generate_answer_success(mock_get_client, sample_results):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.text = "The Eiffel Tower is in Paris, which is the capital of France."
    mock_client.models.generate_content.return_value = mock_response
    
    query = "Where is the Eiffel Tower?"
    result = generate_answer(query, sample_results)
    
    # Check that client was called with correct model and arguments
    mock_client.models.generate_content.assert_called_once()
    call_kwargs = mock_client.models.generate_content.call_args.kwargs
    assert call_kwargs["model"] == config.GENERATION_MODEL
    assert "Where is the Eiffel Tower?" in call_kwargs["contents"]
    
    # Check result
    assert isinstance(result, GenerationResult)
    assert result.answer == "The Eiffel Tower is in Paris, which is the capital of France."
    assert result.source_chunks == sample_results

@patch("sourcex.generation.rag.get_generation_client")
def test_generate_answer_api_error(mock_get_client, sample_results):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_client.models.generate_content.side_effect = APIError("429 Quota exceeded", 429)
    
    with pytest.raises(GenerationError, match="Gemini API Error"):
        generate_answer("Where is the Eiffel Tower?", sample_results)

@patch("sourcex.generation.rag.get_generation_client")
def test_generate_answer_empty_response(mock_get_client, sample_results):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.text = ""
    mock_client.models.generate_content.return_value = mock_response
    
    with pytest.raises(GenerationError, match="Received an empty response from the generation model"):
        generate_answer("Where is the Eiffel Tower?", sample_results)

@patch("sourcex.retrieval.embeddings.get_embedding_client")
@patch("sourcex.generation.rag.get_generation_client")
def test_rag_end_to_end_mocked(mock_get_gen_client, mock_get_emb_client, tmp_path):
    # 1. Setup minimal dummy PDF using PyMuPDF (fitz)
    import fitz
    pdf_path = tmp_path / "dummy.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "The capital of France is Paris.")
    doc.save(str(pdf_path))
    doc.close()
    
    # 2. Extract
    from sourcex.extraction import extract_pdf
    pages = extract_pdf(str(pdf_path))
    
    # 3. Clean
    from sourcex.cleaning import clean_pages
    cleaned_pages = clean_pages(pages)
    
    # 4. Chunk
    from sourcex.chunking import chunk_pages
    final_chunks = chunk_pages(cleaned_pages)
    
    # 6. Embed (Mocked)
    mock_emb_client = MagicMock()
    mock_get_emb_client.return_value = mock_emb_client
    mock_emb_response = MagicMock()
    emb_val = MagicMock()
    emb_val.values = [0.1] * config.EMBEDDING_DIMENSIONS
    mock_emb_response.embeddings = [emb_val]
    mock_emb_client.models.embed_content.return_value = mock_emb_response
    
    from sourcex.retrieval.embeddings import embed_chunks
    embedded = embed_chunks(final_chunks)
    
    # 7. Index
    from sourcex.retrieval.index import VectorStore
    vs = VectorStore(config.EMBEDDING_DIMENSIONS)
    vs.add_chunks(embedded)
    
    # 8. Retrieve (Mocked embedding query)
    from sourcex.retrieval.retriever import Retriever
    retriever = Retriever(vs)
    
    mock_query_emb_response = MagicMock()
    q_emb_val = MagicMock()
    q_emb_val.values = [0.1] * config.EMBEDDING_DIMENSIONS
    mock_query_emb_response.embeddings = [q_emb_val]
    mock_emb_client.models.embed_content.side_effect = [mock_emb_response, mock_query_emb_response]
    
    results = retriever.search("What is the capital of France?")
    
    # 9. Generate (Mocked)
    mock_gen_client = MagicMock()
    mock_get_gen_client.return_value = mock_gen_client
    mock_gen_response = MagicMock()
    mock_gen_response.text = "Paris"
    mock_gen_client.models.generate_content.return_value = mock_gen_response
    
    generation_result = generate_answer("What is the capital of France?", results)
    
    assert generation_result.answer == "Paris"
    assert len(generation_result.source_chunks) == 1
    assert "capital of France is Paris" in generation_result.source_chunks[0].chunk.text
