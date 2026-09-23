# RAG DESIGN — SourceX

Owns the retrieval-side design decisions referenced from `ARCHITECTURE.md`. Filled in as each task lands — do not pre-document a decision before the task that makes it is done.

## Chunking (T004)
- Strategy: Simple character-based sliding window (this is a simple baseline, not semantic chunking).
- Size & Overlap: `CHUNK_SIZE = 1000` characters, `CHUNK_OVERLAP = 200` characters.
- Reasoning: 1000 characters provides enough density for a complete thought/paragraph without exploding context windows downstream. The 200-character overlap ensures that sentences or concepts split across boundary edges are not lost, preserving retrieval context.
- Limitations: Character-based splitting is naïve; hard character boundaries can split words/sentences mid-way. Output is deterministic and page attribution is strictly preserved.

## Metadata schema (T005)
- Strategy: Native Python `@dataclass` pairing `text` with `ChunkMetadata`. This provides a structured dataclass with type annotations and predictable attribute access (it does not perform runtime type validation).
- Schema fields: 
  * `text` — chunk content
  * `document_id` — stable document identifier
  * `source_file` — original source filename
  * `page_number` — 1-indexed human-readable page
  * `chunk_index` — deterministic chunk position
- Reasoning: These fields are the absolute minimum required to link a semantic snippet back to a verifiable source document and specific location for citation generation downstream.

## Embeddings (T006)
- SDK: `google-genai`
- Model: `gemini-embedding-2` (configured via `Config` as `EMBEDDING_MODEL`).
- Dimensionality: `768` (configured via `Config` as `EMBEDDING_DIMENSIONS`).
- Embedding Input Representation: Document chunks are embedded using the format "title: none | text: {chunk_text}" as required by `gemini-embedding-2`. (T008 must format queries using the corresponding query instruction).
- Error Handling: All `APIError` exceptions from the provider are caught and wrapped into a domain-specific `EmbeddingError`.
- Limitations: API rate limits and network latency. Mocks are used for unit tests to prevent network dependency.

## Vector index & persistence strategy (T007)
Render's local filesystem is **ephemeral** — anything written to disk can vanish on restart/redeploy. FAISS itself has no built-in remote persistence, so the index cannot be treated as permanent local state.

**Implemented approach (T007):**
- Uses `faiss-cpu` with `IndexFlatIP` (exact inner-product search, acting as cosine similarity for normalized embeddings).
- Uses `IndexIDMap` to map FAISS IDs back to original unmodified `Chunk` metadata in a standard Python dictionary.
- Supports local development persistence via `.faiss` and `metadata.json` files.
- The production FAISS index is designed to be a **rebuildable cache**: built in memory at app startup or on first query from persisted embeddings.
- This avoids introducing a hosted vector database purely to solve a deployment quirk — FAISS stays the retrieval engine; only its persistence story changes.

## Retrieval (T008)
- Top-K similarity search; TBD: K value and similarity metric (cosine vs. L2), to be recorded once implemented.

## LangGraph grading & rewriting (T013–T014)
- TBD: what "sufficient evidence" means concretely (e.g. similarity threshold, minimum chunk count) — record the actual rule once implemented, and the retry cap chosen to guarantee loop termination.

## Citation verification (T016)
- TBD: verification method (e.g. checking generated claim text overlaps cited chunk content) once implemented.
