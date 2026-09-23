import os
import json
import faiss
import numpy as np
from dataclasses import dataclass, asdict
from typing import List, Dict

from sourcex.config import config
from sourcex.metadata import Chunk, ChunkMetadata
from sourcex.retrieval.embeddings import EmbeddedChunk

@dataclass
class SearchResult:
    chunk: Chunk
    score: float

class IndexDimensionError(ValueError):
    """Raised when an embedding or query vector has the wrong dimensionality."""
    pass

class VectorStore:
    """
    A FAISS-backed exact-search vector store.
    Uses faiss.IndexFlatIP for Inner Product (Cosine Similarity for normalized vectors).
    Maintains a mapping between FAISS integer IDs and original Chunk objects.
    """
    def __init__(self, dimension: int = config.EMBEDDING_DIMENSIONS):
        self.dimension = dimension
        # Use IndexIDMap to assign our own integer IDs rather than auto-increment
        self.index = faiss.IndexIDMap(faiss.IndexFlatIP(dimension))
        self.chunk_mapping: Dict[int, Chunk] = {}
        self.next_id: int = 0
        
    def add_chunks(self, embedded_chunks: List[EmbeddedChunk]) -> None:
        """
        Adds a list of EmbeddedChunks to the FAISS index and local mapping.
        """
        if not embedded_chunks:
            return
            
        embeddings = []
        for ec in embedded_chunks:
            if len(ec.embedding) != self.dimension:
                raise IndexDimensionError(f"Expected dimension {self.dimension}, got {len(ec.embedding)}")
            embeddings.append(ec.embedding)
            
        embeddings_np = np.array(embeddings, dtype=np.float32)
        
        # Generate sequential IDs for this batch
        count = len(embedded_chunks)
        ids = np.arange(self.next_id, self.next_id + count, dtype=np.int64)
        
        # Add to FAISS index
        self.index.add_with_ids(embeddings_np, ids)
        
        # Add to mapping
        for faiss_id, ec in zip(ids, embedded_chunks):
            # We store the original Chunk, leaving it completely unmodified
            self.chunk_mapping[int(faiss_id)] = ec.chunk
            
        self.next_id += count

    def search(self, query_vector: List[float], k: int = 5) -> List[SearchResult]:
        """
        Searches the FAISS index for the top k chunks matching the query vector.
        """
        if self.index.ntotal == 0 or k <= 0:
            return []
            
        if len(query_vector) != self.dimension:
            raise IndexDimensionError(f"Expected query dimension {self.dimension}, got {len(query_vector)}")
            
        # Adjust k if it's larger than the index size
        actual_k = min(k, self.index.ntotal)
        
        query_np = np.array([query_vector], dtype=np.float32)
        
        # faiss.IndexIDMap search returns float32 scores and int64 IDs
        scores, ids = self.index.search(query_np, actual_k)
        
        results = []
        for score, faiss_id in zip(scores[0], ids[0]):
            faiss_id = int(faiss_id)
            if faiss_id == -1 or faiss_id not in self.chunk_mapping:
                continue
            
            chunk = self.chunk_mapping[faiss_id]
            results.append(SearchResult(chunk=chunk, score=float(score)))
            
        return results

    def save(self, directory: str) -> None:
        """
        Saves the FAISS index and JSON metadata to a directory for local dev persistence.
        """
        os.makedirs(directory, exist_ok=True)
        
        faiss_path = os.path.join(directory, "index.faiss")
        faiss.write_index(self.index, faiss_path)
        
        metadata_path = os.path.join(directory, "metadata.json")
        
        # Serialize the chunk mapping
        serialized_mapping = {}
        for faiss_id, chunk in self.chunk_mapping.items():
            serialized_mapping[str(faiss_id)] = {
                "text": chunk.text,
                "metadata": asdict(chunk.metadata)
            }
            
        data = {
            "dimension": self.dimension,
            "next_id": self.next_id,
            "chunk_mapping": serialized_mapping
        }
        
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, directory: str) -> None:
        """
        Loads the FAISS index and JSON metadata from a directory.
        """
        faiss_path = os.path.join(directory, "index.faiss")
        metadata_path = os.path.join(directory, "metadata.json")
        
        if not os.path.exists(faiss_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Index or metadata file not found in {directory}")
            
        self.index = faiss.read_index(faiss_path)
        
        with open(metadata_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if data["dimension"] != self.dimension:
            raise IndexDimensionError(f"Loaded index dimension {data['dimension']} does not match expected {self.dimension}")
            
        self.next_id = data["next_id"]
        
        self.chunk_mapping = {}
        for str_id, chunk_data in data["chunk_mapping"].items():
            meta_dict = chunk_data["metadata"]
            meta = ChunkMetadata(
                document_id=meta_dict["document_id"],
                source_file=meta_dict["source_file"],
                page_number=meta_dict["page_number"],
                chunk_index=meta_dict["chunk_index"]
            )
            self.chunk_mapping[int(str_id)] = Chunk(
                text=chunk_data["text"],
                metadata=meta
            )
