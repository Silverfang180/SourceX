# LEARNING NOTES — SourceX

This file accumulates concept explanations as they come up during the build, each written to interview-defensible depth. Structure per concept:

1. What it is
2. Why it is needed
3. How it works
4. Where it fits in SourceX
5. What alternatives exist
6. What trade-offs exist
7. How to explain it in an interview

Entries are added when a concept is actually implemented and understood — not pre-written ahead of the work (see `DEVELOPMENT_RULES.md`: don't document what isn't built yet).

## Status
No entries yet. First entries will land with Phase 1 (PDF extraction, chunking, embeddings, FAISS retrieval) as each is implemented.

## Planned first entries (Day 1)
- Text extraction from PDFs — what's actually hard about it
- Chunking strategy — why chunk size/overlap matters, how it was chosen for SourceX
- Embeddings — what a vector actually encodes, why cosine/L2 distance is a proxy for meaning
- FAISS — what an approximate nearest-neighbor index is doing, why it's needed at scale
- Retrieval — what "semantic search" means mechanically, and where it can silently fail

## Interview question bank (living list)
Populated and answered from the actual implementation as phases complete — see `PRD.md` §15 for the seed list (why FAISS, why embeddings are needed, how retrieval works, why chunk size was chosen, what happens when retrieval fails, why LangChain, why LangGraph, why LangGraph suits conditional workflows, how query rewriting works, how citations are generated, how the RAG system was evaluated, what its limitations are).
