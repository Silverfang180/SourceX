from typing import List
from dataclasses import dataclass
from google import genai
from google.genai.errors import APIError

from sourcex.config import config
from sourcex.retrieval.index import SearchResult

class GenerationError(Exception):
    """Domain-specific error for generation failures."""
    pass

@dataclass
class GenerationResult:
    """Contains the generated answer and the chunks used as context."""
    answer: str
    source_chunks: List[SearchResult]

def get_generation_client() -> genai.Client:
    """Initializes and returns the configured Gemini Client."""
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=config.GEMINI_API_KEY)

def build_prompt(query: str, results: List[SearchResult]) -> str:
    """Builds a grounded prompt using the retrieved context."""
    if not results:
        context_str = "No relevant context found."
    else:
        context_parts = []
        for i, res in enumerate(results):
            # Using 1-based indexing for readability
            context_parts.append(f"[Document {i+1}]\n{res.chunk.text}")
        context_str = "\n\n".join(context_parts)
        
    return (
        f"Answer the user's question based on the following context. "
        f"If you don't know the answer or the context doesn't provide enough information, "
        f"just say you don't know. Do not invent information.\n\n"
        f"Context:\n{context_str}\n\n"
        f"Question: {query}"
    )

def generate_answer(query: str, results: List[SearchResult]) -> GenerationResult:
    """
    Generates an answer to the query using the provided SearchResults as context.
    
    Args:
        query: The user's question.
        results: The retrieved relevant chunks.
        
    Returns:
        GenerationResult containing the text answer and the exact sources used.
    """
    client = get_generation_client()
    prompt = build_prompt(query, results)
    
    try:
        response = client.models.generate_content(
            model=config.GENERATION_MODEL,
            contents=prompt
        )
        
        if not response.text:
            raise GenerationError("Received an empty response from the generation model.")
            
        return GenerationResult(
            answer=response.text,
            source_chunks=results
        )
    except APIError as e:
        raise GenerationError(f"Gemini API Error: {str(e)}") from e
