import os
from sourcex.config import config
from sourcex.generation.rag import build_prompt, generate_answer
from sourcex.metadata import Chunk, ChunkMetadata
from sourcex.retrieval.embeddings import EmbeddedChunk
from sourcex.retrieval.index import SearchResult

def run_t009_smoke_test():
    print("Running T009 Live Smoke Test...")
    
    # 1. Load config and verify key
    if not config.GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not set.")
        return
    print(f"API Key loaded (length: {len(config.GEMINI_API_KEY)} chars)")
    
    # 2. Create tiny grounded context
    chunk = Chunk(
        text="The capital of the fictional country of Xylar is Zantropolis.",
        metadata=ChunkMetadata(
            document_id="doc_1",
            source_file="xylar_info.txt",
            page_number=1,
            chunk_index=0
        )
    )
    search_result = SearchResult(chunk=chunk, score=0.99)
    
    results = [search_result]
    question = "What is the capital of Xylar?"
    
    # 3. Build prompt
    prompt = build_prompt(question, results)
    
    # 4. Generate answer
    print(f"Sending question: {question}")
    result = generate_answer(question, results)
    answer = result.answer
    used_chunks = result.source_chunks
    
    print("\n--- Answer ---")
    print(answer)
    print("--------------")
    
    # 5. Verifications
    assert answer, "Answer should not be empty"
    assert "Zantropolis" in answer, "Answer did not contain expected explicit information"
    assert len(used_chunks) == 1, "Should have 1 used chunk"
    assert used_chunks[0].chunk.metadata.document_id == "doc_1", "Source chunk reference lost"
    
    print("T009 Smoke Test PASSED.\n")

if __name__ == "__main__":
    run_t009_smoke_test()
