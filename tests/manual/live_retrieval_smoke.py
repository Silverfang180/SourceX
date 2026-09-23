import sys
import os

# Ensure src is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from sourcex.config import config
from sourcex.metadata import Chunk, ChunkMetadata
from sourcex.retrieval.embeddings import embed_chunks
from sourcex.retrieval.index import VectorStore
from sourcex.retrieval.retriever import Retriever

def main():
    if not config.GEMINI_API_KEY:
        print("FAIL: GEMINI_API_KEY is not set.")
        sys.exit(1)
        
    print("--- LIVE RETRIEVAL SMOKE TEST ---")
    
    # 1. Create a tiny dataset with clearly different topics
    print("Creating tiny dataset...")
    c1 = Chunk(
        text="The mitochondria is the powerhouse of the cell, generating most of the chemical energy needed to power the cell's biochemical reactions.",
        metadata=ChunkMetadata("doc_bio", "biology.pdf", 1, 0)
    )
    c2 = Chunk(
        text="Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.",
        metadata=ChunkMetadata("doc_cs", "python.pdf", 1, 0)
    )
    c3 = Chunk(
        text="The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. It is named after the engineer Gustave Eiffel.",
        metadata=ChunkMetadata("doc_geo", "paris.pdf", 1, 0)
    )
    
    # 2. Generate document embeddings via real Gemini API
    print("Generating document embeddings via Gemini...")
    try:
        embedded_chunks = embed_chunks([c1, c2, c3])
    except Exception as e:
        print(f"FAIL: Real document embedding failed: {e}")
        sys.exit(1)
        
    # 3. Build VectorStore
    print("Building FAISS VectorStore...")
    store = VectorStore(dimension=config.EMBEDDING_DIMENSIONS)
    store.add_chunks(embedded_chunks)
    
    # 4. Initialize Retriever
    retriever = Retriever(store)
    
    # 5. Ask a question and retrieve
    query = "Where is the Eiffel Tower located?"
    print(f"\nQuery: '{query}'")
    print("Executing retrieval...")
    
    try:
        results = retriever.search(query, k=2)
    except Exception as e:
        print(f"FAIL: Real query embedding/retrieval failed: {e}")
        sys.exit(1)
        
    # 6. Verify results
    if not results:
        print("FAIL: No results returned.")
        sys.exit(1)
        
    top_result = results[0]
    
    print("\n--- RESULTS ---")
    for i, res in enumerate(results):
        print(f"[{i+1}] Score: {res.score:.4f} | Source: {res.chunk.metadata.source_file} (Page {res.chunk.metadata.page_number})")
        print(f"    Text: {res.chunk.text[:80]}...")
        
    # We expect the Paris chunk (c3) to be the top result
    if top_result.chunk.metadata.document_id == "doc_geo":
        print("\nSUCCESS! The expected relevant chunk was retrieved first.")
    else:
        print(f"\nFAIL! Expected 'doc_geo' to be top, but got '{top_result.chunk.metadata.document_id}'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
