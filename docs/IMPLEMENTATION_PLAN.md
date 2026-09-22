# IMPLEMENTATION PLAN — SourceX

3-day MVP, then evaluation/production phases continue as scope allows. One phase should be solid before the next starts.

## Day 1 — RAG fundamentals (no framework)

**Objective:** Understand and implement RAG mechanics directly, without LangChain, so nothing later is a black box.

**Pipeline target:**
```
PDF → extraction → cleaning → chunking → metadata → embeddings → FAISS → retrieval → basic RAG generation
```

**Sequence:**
1. Repository foundation (structure, env, dependency setup)
2. PDF text extraction
3. Text cleaning
4. Chunking (with overlap; chunk size is a decision to make deliberately, not default blindly)
5. Metadata attachment (source file, page, chunk index)
6. Embedding generation
7. FAISS indexing
8. Semantic retrieval (query → embedding → nearest chunks)
9. Basic RAG generation (retrieved context + question → Gemini → answer)

**Explicit exclusions for Day 1:** no LangChain, no LangGraph, no frontend.

## Day 2 — LangChain + LangGraph

- Rebuild the Day 1 pipeline using LangChain, mapping each manual step to its LangChain equivalent
- Introduce LangGraph state, nodes, edges, and conditional edges
- Target workflow:
```
START → Analyze Query → Retrieve → Grade Evidence
  ├── Good → Generate
  └── Poor → Rewrite Query → Retrieve (loop) → Grade
→ Generate → Verify Sources → END
```

## Day 3 — Portfolio-quality application

- Multi-document support
- Citations
- Conversational context
- Tool calling (limited, deliberate set)
- Evaluation (initial pass)
- FastAPI endpoints
- Next.js UI
- Docker
- Tests
- README + screenshots/demo
- Interview preparation notes

**Priority rule:** if the core (Days 1–2) is incomplete, correctness there takes priority over adding Day 3 features.

## Beyond Day 3 (continued as scope allows)

- **Phase 4 — Source grounding:** citations, page references, evidence verification, unsupported-answer handling
- **Phase 5 — Tools:** calculator, document search, metadata/document inspection
- **Phase 6 — Evaluation:** Recall@K, MRR where appropriate, answer relevance, faithfulness/groundedness, citation correctness, latency, token usage, cost
- **Phase 7 — Production engineering:** FastAPI, PostgreSQL, Docker, Next.js, testing, logging, configuration, deployment

## Current status
Planning stage complete for Day 1. No implementation started. Next concrete step is `T001 Repository foundation` in `TASKS.md`.
