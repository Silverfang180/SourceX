from typing import Any, Dict
from langchain_core.retrievers import BaseRetriever
from sourcex.graph.state import GraphState

def analyze_query(state: GraphState) -> Dict[str, Any]:
    """
    T012: Validates and normalizes the user's query.
    Produces the formatted query needed by the embedding model.
    """
    query = state.get("query", "").strip()
    if not query:
        raise ValueError("Query cannot be empty.")
        
    # The embedding step (T008) owns formatting the query for Gemini.
    # Here, we only validate and normalize the query.
    normalized_query = query
    
    return {"search_query": normalized_query}

class RetrieveContextNode:
    """
    T012: Retrieves context from the vector store using a LangChain retriever.
    Designed with dependency injection to allow testing without live API calls.
    """
    def __init__(self, retriever: BaseRetriever):
        self.retriever = retriever
        
    def __call__(self, state: GraphState) -> Dict[str, Any]:
        # Fall back to raw query if search_query is somehow missing
        search_query = state.get("search_query") or state.get("query", "")
        
        # We allow retrieval failures to propagate as instructed
        docs = self.retriever.invoke(search_query)
        
        return {"retrieved_chunks": docs}
