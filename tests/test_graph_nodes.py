import pytest
from langchain_core.documents import Document
from sourcex.graph.nodes import analyze_query, RetrieveContextNode
from sourcex.graph.state import GraphState
from tests.test_graph import MockRetriever

def test_analyze_query_valid():
    """T012: Verify analyze_query normalizes the query properly."""
    state = {"query": "What is Xylar?"}
    update = analyze_query(state)
    
    assert "search_query" in update
    assert update["search_query"] == "What is Xylar?"

def test_analyze_query_empty():
    """T012: Verify analyze_query handles empty input safely."""
    with pytest.raises(ValueError, match="Query cannot be empty"):
        analyze_query({"query": "   "})
        
def test_retrieve_context_success():
    """T012: Verify retrieve_context invokes retriever and stores chunks."""
    mock_docs = [
        Document(page_content="Doc 1", metadata={"score": 0.9}),
        Document(page_content="Doc 2", metadata={"score": 0.8})
    ]
    retriever = MockRetriever(mock_docs=mock_docs)
    node = RetrieveContextNode(retriever)
    
    # Simulate state after analyze_query
    state = {
        "query": "What is Xylar?",
        "search_query": "What is Xylar?"
    }
    
    update = node(state)
    assert "retrieved_chunks" in update
    assert len(update["retrieved_chunks"]) == 2
    assert update["retrieved_chunks"][0].page_content == "Doc 1"

def test_retrieve_context_empty_results():
    """T012: Verify retrieve_context safely handles zero results."""
    retriever = MockRetriever(mock_docs=[])
    node = RetrieveContextNode(retriever)
    
    update = node({"query": "Unknown", "search_query": "Unknown"})
    assert "retrieved_chunks" in update
    assert len(update["retrieved_chunks"]) == 0

class FailingRetriever(MockRetriever):
    def _get_relevant_documents(self, query: str, *, run_manager=None):
        raise RuntimeError("FAISS connection lost")

def test_retrieve_context_propagates_failure():
    """T012: Verify retrieve_context propagates retrieval failures."""
    node = RetrieveContextNode(FailingRetriever())
    
    with pytest.raises(RuntimeError, match="FAISS connection lost"):
        node({"query": "test"})
