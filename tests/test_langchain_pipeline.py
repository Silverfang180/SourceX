import pytest
from unittest.mock import patch, MagicMock

from sourcex.config import config
from sourcex.langchain_pipeline.pipeline import (
    extract_documents,
    build_langchain_vectorstore,
    create_rag_chain,
    run_pipeline
)
from langchain_core.documents import Document

@pytest.fixture
def dummy_pdf_path(tmp_path):
    import fitz
    pdf_path = tmp_path / "dummy.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "LangChain is a framework for developing applications powered by language models.")
    doc.save(str(pdf_path))
    doc.close()
    return str(pdf_path)

def test_extract_documents(dummy_pdf_path):
    docs = extract_documents(dummy_pdf_path)
    assert len(docs) == 1
    assert "LangChain is a framework" in docs[0].page_content
    assert docs[0].metadata["page_number"] == 1
    assert docs[0].metadata["document_id"] == "dummy.pdf"
    assert docs[0].metadata["source_file"] == "dummy.pdf"

@patch("langchain_google_genai.GoogleGenerativeAIEmbeddings.embed_documents")
def test_build_langchain_vectorstore(mock_embed):
    # Mock embedding to return a zero vector of correct dim
    mock_embed.return_value = [[0.0] * config.EMBEDDING_DIMENSIONS]
    
    docs = [Document(page_content="Test document content", metadata={"page_number": 1, "document_id": "test", "source_file": "test.pdf"})]
    vs = build_langchain_vectorstore(docs)
    
    assert vs is not None
    # Check that embed_documents was called with the exact formatted text expected by gemini-embedding-2
    mock_embed.assert_called_once()
    texts = mock_embed.call_args[0][0]
    assert texts[0] == "title: none | text: Test document content"

@patch("langchain_google_genai.GoogleGenerativeAIEmbeddings.embed_documents")
@patch("langchain_google_genai.GoogleGenerativeAIEmbeddings.embed_query")
@patch("langchain_google_genai.ChatGoogleGenerativeAI.invoke")
def test_run_pipeline_parity(mock_llm_invoke, mock_embed_query, mock_embed_docs, dummy_pdf_path):
    # Setup mocks
    mock_embed_docs.return_value = [[0.1] * config.EMBEDDING_DIMENSIONS]
    mock_embed_query.return_value = [0.1] * config.EMBEDDING_DIMENSIONS
    
    from langchain_core.messages import AIMessage
    mock_llm_invoke.return_value = AIMessage(content="LangChain is a framework.")
    
    result = run_pipeline(dummy_pdf_path, "What is LangChain?")
    
    # 1. verify generation equivalent to T009
    assert result["answer"] == "LangChain is a framework."
    
    # 2. verify chunk source references are returned
    assert len(result["source_documents"]) == 1
    source_doc = result["source_documents"][0]
    assert "LangChain is a framework for developing applications" in source_doc.page_content
    assert source_doc.metadata["document_id"] == "dummy.pdf"
    
    # 3. verify query was formatted as strictly required by gemini-embedding-2 in T008
    mock_embed_query.assert_called_with("task: question answering | query: What is LangChain?")
    assert mock_embed_query.call_count == 2
