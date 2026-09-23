from typing import List

from sourcex.retrieval.index import VectorStore, SearchResult
from sourcex.retrieval.embeddings import embed_query, EmbeddingError

class Retriever:
    """
    Orchestrates the retrieval flow by connecting query embedding to the FAISS VectorStore.
    """
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        
    def search(self, query: str, k: int = 5) -> List[SearchResult]:
        """
        Takes a raw user query string, embeds it using the Question Answering instruction,
        and retrieves the nearest K chunks ranked by similarity score from the VectorStore.
        
        Args:
            query: The user's question string.
            k: The maximum number of results to retrieve.
            
        Returns:
            A list of SearchResult objects containing the chunks and their FAISS scores.
        """
        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty.")
            
        if k <= 0:
            return []
            
        # 1. Embed query
        # This can raise EmbeddingError, which we allow to propagate.
        query_vector = embed_query(query)
        
        # 2. Search FAISS index
        # This will return the mapped Chunk objects + inner product scores.
        results = self.vector_store.search(query_vector, k=k)
        
        return results
