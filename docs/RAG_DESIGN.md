# RAG DESIGN — SourceX

Owns the retrieval-side design decisions referenced from `ARCHITECTURE.md`. Filled in as each task lands — do not pre-document a decision before the task that makes it is done.

## Chunking (T004)
- Strategy: TBD when T004 is implemented — record chosen chunk size, overlap, and splitting method (character/token-based) here, with the reasoning (why that size trades off recall vs. context-window/cost).

## Metadata schema (T005)
- Per-chunk fields: `source_file`, `page_number`, `chunk_index`, `document_id` (TBD to confirm final field set once T005 lands).

## Embeddings (T006)
- Model: Gemini embedding API (specific model name via `Config`, not hardcoded).
- TBD: dimensionality, batching approach, cost/latency notes.

## Vector index & persistence strategy (T007) — important
Render's local filesystem is **ephemeral** — anything written to disk can vanish on restart/redeploy. FAISS itself has no built-in remote persistence, so the index cannot be treated as permanent local state.

**Chosen approach (to confirm at T007/T023):**
- Chunk text + metadata + embeddings are the durable source of truth, persisted in PostgreSQL (Supabase) and/or alongside the PDF in Cloudflare R2 — not only in the FAISS index file.
- The FAISS index itself is treated as a **rebuildable cache**: built in memory (or on ephemeral disk) at app startup or on first query per document, from the persisted embeddings.
- This avoids introducing a hosted vector database purely to solve a deployment quirk — FAISS stays the retrieval engine; only its persistence story changes.
- Trade-off: rebuild adds latency on cold start — acceptable for a portfolio-scale MVP; would need revisiting only if this became a real, high-traffic product.

## Retrieval (T008)
- Top-K similarity search; TBD: K value and similarity metric (cosine vs. L2), to be recorded once implemented.

## LangGraph grading & rewriting (T013–T014)
- TBD: what "sufficient evidence" means concretely (e.g. similarity threshold, minimum chunk count) — record the actual rule once implemented, and the retry cap chosen to guarantee loop termination.

## Citation verification (T016)
- TBD: verification method (e.g. checking generated claim text overlaps cited chunk content) once implemented.
