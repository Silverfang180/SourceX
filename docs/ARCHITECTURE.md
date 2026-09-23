# ARCHITECTURE — SourceX

Companion docs: `RAG_DESIGN.md` (retrieval/chunking/persistence detail), `EVALUATION_PLAN.md` (metrics), `DEPLOYMENT.md` (infrastructure detail). This document is the system-level overview; those own their subject in depth.

## System architecture

```
Browser
  ↓
Next.js frontend (Vercel)
  ↓  HTTPS
FastAPI backend (Dockerized, Render Free)
  ↓
Auth + user/document isolation layer
  ↓
LangGraph orchestration (real runtime component, not a demo)
  ↓                              ↓
LangChain retrieval/generation   PostgreSQL (Supabase)
  ↓                              — users, document metadata, chunk metadata
Gemini API (embeddings + LLM)
  ↓
FAISS index (persistence strategy: see RAG_DESIGN.md)
  ↓
Grounded response + page-level citations + verification status
```

Cloudflare R2 holds the original PDFs — the backend's local filesystem is never treated as permanent storage (Render's disk is ephemeral).

## RAG pipeline (core mechanics)

```
PDF file
  → text extraction         (PyMuPDF: raw text + page numbers)     [T002 — done]
  → cleaning                (strip noise, normalize whitespace)     [T003 — done]
  → chunking                (overlapping chunks)                    [T004 — next]
  → metadata                (source file, page, chunk index)        [T005]
  → embeddings               (Gemini embedding API)                 [T006]
  → FAISS index                                                      [T007]
  → retrieval                (query → embedding → nearest chunks)   [T008]
  → basic generation                                                 [T009]
```
T001–T009 are built without a framework first, so the mechanics are never a black box, then genuinely rebuilt/orchestrated with LangChain (T010) and LangGraph (T011–T016).

## LangGraph workflow (must be real, not decorative)

```
START
  ↓
analyze_query
  ↓
retrieve_context
  ↓
grade_context
  ├── sufficient → generate_answer → verify_citations → END
  └── insufficient → rewrite_query → retrieve_context (loop back to grade_context)
```

Simplify where necessary, but conditional routing and the retry loop must be functionally real — this is the centerpiece LangGraph demonstration for the project.

## Security architecture

```
authenticated_user_id + requested_document_id → verify ownership → allow access
```
Applies to every protected operation: PDFs, metadata, chunks, retrieval results, generated results, deletion, downloads. Enforced server-side, never trusting a document ID alone. Secrets (Gemini key, DB credentials) never reach the frontend.

## Architecture principles (priority order)
1. Correctness
2. Simplicity
3. Modularity
4. Testability
5. Security
6. Explainability
7. Deployment practicality

Deliberately excluded: Kubernetes, microservices, GPU infrastructure, large local models, multiple vector databases, multiple LLM providers, complex agent swarms, excessive tools, unnecessary distributed systems. Every technology choice must have a clear, statable purpose in SourceX.

## Current status
Complete and verified: **T001, T002, T003**. Next: **T004 — Chunking**. No retrieval, LangChain/LangGraph integration, backend API, database, auth, frontend, or deployment infrastructure exists yet.
