from typing import List
from dataclasses import dataclass
from google import genai
from google.genai import types
from google.genai.errors import APIError

from sourcex.config import config
from sourcex.metadata import Chunk

class EmbeddingError(Exception):
    """Domain-specific error for embedding failures."""
    pass

@dataclass
class EmbeddedChunk:
    """Pairs a chunk with its computed embedding vector."""
    chunk: Chunk
    embedding: List[float]

def get_embedding_client() -> genai.Client:
    """Initializes and returns the configured Gemini Client."""
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured.")
    return genai.Client(api_key=config.GEMINI_API_KEY)

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Accepts a list of texts and returns one vector per input.
    N inputs -> N independent embeddings, preserving input order.
    """
    if not texts:
        return []

    client = get_embedding_client()
    
    try:
        # For gemini-embedding-2, document retrieval expects: "title: none | text: {text}"
        formatted_texts = [f"title: none | text: {text}" for text in texts]
        
        response = client.models.embed_content(
            model=config.EMBEDDING_MODEL,
            contents=formatted_texts,
            config=types.EmbedContentConfig(
                output_dimensionality=config.EMBEDDING_DIMENSIONS
            )
        )
        
        # Verify the response shape matches our expectations
        if not response.embeddings or len(response.embeddings) != len(texts):
            got_count = len(response.embeddings) if response.embeddings else 0
            raise EmbeddingError(f"Expected {len(texts)} embeddings, got {got_count}")
            
        vectors = []
        for emb in response.embeddings:
            if not emb.values:
                raise EmbeddingError("Received an embedding with missing vector values.")
            if len(emb.values) != config.EMBEDDING_DIMENSIONS:
                raise EmbeddingError(f"Expected dimensionality {config.EMBEDDING_DIMENSIONS}, got {len(emb.values)}")
            vectors.append(emb.values)
            
        return vectors

    except APIError as e:
        # Wrap provider exceptions
        raise EmbeddingError(f"Gemini API Error: {str(e)}") from e
    except Exception as e:
        # Catch unexpected errors to prevent raw provider exceptions from leaking
        if isinstance(e, EmbeddingError):
            raise
        raise EmbeddingError(f"Failed to generate embeddings: {str(e)}") from e

def embed_chunks(chunks: List[Chunk]) -> List[EmbeddedChunk]:
    """
    Pairs each original Chunk with its embedding.
    """
    if not chunks:
        return []
        
    texts = [chunk.text for chunk in chunks]
    vectors = embed_texts(texts)
    
    return [EmbeddedChunk(chunk=c, embedding=v) for c, v in zip(chunks, vectors)]
