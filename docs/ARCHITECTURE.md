# ARCHITECTURE — SourceX

This document describes the *target* architecture across all phases, and which parts exist today. Phases build on each other — do not implement a later phase's component before the current phase is done (see `IMPLEMENTATION_PLAN.md`).

## Architectural phases (high level)

```
Phase 1: Raw RAG (no framework)
Phase 2: LangChain rebuild
Phase 3: LangGraph stateful orchestration
Phase 4: Source grounding (citations, verification)
Phase 5: Tool calling
Phase 6: Evaluation
Phase 7: Production engineering (API, DB, containerization, UI)
```

## Phase 1 — Core RAG pipeline (Day 1 target)

```
PDF file
  → text extraction         (pull raw text + page numbers out of the PDF)
  → cleaning                (strip noise: headers/footers, broken whitespace, ligatures)
  → chunking                (split into retrieval-sized units, with overlap)
  → metadata attachment     (source file, page number, chunk index)
  → embeddings              (chunk text → vector)
  → vector index (FAISS)    (store vectors for similarity search)
  → retrieval                (query → embedding → nearest chunks)
  → context construction    (assemble retrieved chunks into a prompt context)
  → LLM call                (Gemini API, given question + context)
  → grounded answer         (answer + which chunks it came from)
```

This phase is implemented **without LangChain** on purpose — the objective is to understand what a framework's `create_rag_chain()`-style helper is actually doing underneath, so it's never a black box later.

## Phase 2 — LangChain

Same pipeline, rebuilt using LangChain's document loaders, text splitters, embedding wrappers, vector store integration, and chain composition. The goal here is translation, not new capability: map each Phase 1 step to its LangChain equivalent and understand exactly what each abstraction is standing in for.

## Phase 3 — LangGraph (Day 2 target)

Introduces state and conditional control flow instead of a fixed linear chain:

```
START
  ↓
Analyze Query
  ↓
Retrieve
  ↓
Grade Evidence
  ├── Good → Generate
  └── Poor → Rewrite Query → Retrieve (loop back to Grade)
  ↓
Generate
  ↓
Verify Sources
  ↓
END
```

Key concepts to understand at this phase, not just use:
- **State** — the data structure threaded through every node (query, retrieved docs, grade result, rewritten query, answer, etc.)
- **Nodes** — functions that read/transform state
- **Edges** — the fixed transitions between nodes
- **Conditional edges** — transitions chosen based on state (e.g. grade result)
- **Loops** — retrieve → grade → rewrite → retrieve until evidence is good enough or a retry limit is hit
- **Graph execution** — how LangGraph actually walks this graph at runtime

## Phase 4 — Source grounding

- Citations tied to specific chunks (source file + page)
- Evidence verification: does the generated answer's claim actually appear in the cited chunk?
- Explicit "unsupported answer" handling when the LLM can't ground a claim in retrieved evidence, instead of silently hallucinating

## Phase 5 — Tools

A small, deliberately limited toolset added to the graph (e.g. calculator, document search/lookup, metadata inspection) — added because they serve the product, not to pad a resume.

## Phase 6 — Evaluation

Metrics computed against the system, not just asserted:
- Retrieval: Recall@K, MRR where applicable
- Generation: answer relevance, faithfulness/groundedness, citation correctness
- Operational: latency, token usage, cost

## Phase 7 — Production engineering

```
Next.js (TypeScript, Tailwind) frontend
        │  HTTP
        ▼
FastAPI backend  ──►  LangGraph orchestration  ──►  Gemini API
        │
        ▼
PostgreSQL (documents, chunks/metadata, evaluation results)
        │
FAISS vector index (local to Phase 1–6; may move into/alongside Postgres later if there's a concrete reason)
```

Containerized with Docker; tested; logged; configured via environment, not hardcoded values.

## Current status
Only this document and the accompanying planning docs exist. No code has been written yet. Phase 1 (Day 1) has not started.
