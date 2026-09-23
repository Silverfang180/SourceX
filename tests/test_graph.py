import pytest
from typing import List
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field
from sourcex.graph.state import GraphState
from sourcex.graph.graph import create_graph

class MockRetriever(BaseRetriever):
    """A deterministic mock retriever for testing."""
    mock_docs: List[Document] = Field(default_factory=list)
    
    def _get_relevant_documents(self, query: str, *, run_manager=None) -> List[Document]:
        return self.mock_docs

def test_graph_state_creation():
    """T011: Verify state can be created with a sample query."""
    state: GraphState = {
        "query": "What is the capital of Xylar?",
        "retrieved_chunks": [],
        "rewritten_query": None,
        "context_grade": None,
        "answer": None,
        "citation_verification": None,
        "retry_count": 0
    }
    
    assert state["query"] == "What is the capital of Xylar?"
    assert state["retrieved_chunks"] == []
    assert state["retry_count"] == 0

def test_graph_compilation():
    """T011: Verify the graph compiles successfully."""
    graph = create_graph(MockRetriever())
    assert graph is not None

def test_graph_execution():
    """T011/T012: Verify the graph executes successfully and preserves state."""
    mock_retriever = MockRetriever(mock_docs=[Document(page_content="Mock content")])
    graph = create_graph(mock_retriever)
    
    initial_state: GraphState = {
        "query": "Sample test query",
        "retrieved_chunks": [],
        "retry_count": 0
    }
    
    final_state = graph.invoke(initial_state)
    
    # Verify execution completes and query is preserved
    assert final_state is not None
    assert final_state["query"] == "Sample test query"
    # verify T012 retrieval actually occurred
    assert len(final_state["retrieved_chunks"]) == 1
    assert final_state["retrieved_chunks"][0].page_content == "Mock content"
    assert final_state["search_query"] == "Sample test query"
