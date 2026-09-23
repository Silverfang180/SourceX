from typing import TypedDict, List, Optional, Any
from langchain_core.documents import Document

class GraphState(TypedDict, total=False):
    """
    Represents the shared state of the SourceX workflow graph.
    """
    query: str
    search_query: Optional[str]
    retrieved_chunks: List[Document]
    
    # Placeholders for future tasks (T013+)
    rewritten_query: Optional[str]
    context_grade: Optional[str]
    answer: Optional[str]
    citation_verification: Optional[str]
    retry_count: int
