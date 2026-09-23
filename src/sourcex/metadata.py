from dataclasses import dataclass

@dataclass
class ChunkMetadata:
    """
    Formal metadata schema attached to each text chunk.
    Ensures page attribution and document origin are permanently linked to the chunk text.
    """
    document_id: str
    source_file: str
    page_number: int
    chunk_index: int

@dataclass
class Chunk:
    """
    Represents a discrete piece of text ready for embedding, paired with its metadata.
    """
    text: str
    metadata: ChunkMetadata
