# IMPLEMENTATION PLAN — SourceX

Dependency-ordered phases. See `TASKS.md` for the task-by-task handoff with acceptance criteria; this document is the phase-level map.

| Phase | Covers | Status |
|---|---|---|
| 1. Document pipeline | Repo foundation, PDF extraction, cleaning, chunking, metadata (T001–T005) | T001–T003 done, T004 next |
| 2. Retrieval foundation | Embeddings, FAISS indexing, retrieval (T006–T008) | Not started |
| 3. Basic RAG | Retriever + prompt + generation, no framework (T009) | Not started |
| 4. LangChain | Real retrieval/generation pipeline via LangChain (T010) | Not started |
| 5. LangGraph | State, conditional routing, query rewriting, context grading, generation, citation verification (T011–T017) | Not started |
| 6. Evaluation | Small evaluation dataset + measurable checks (T018) | Not started |
| 7. Backend/application | FastAPI endpoints, document management, auth, Postgres, user isolation, storage (T019–T023) | Not started |
| 8. Frontend | Next.js: upload, processing status, query, citations, document management (T024) | Not started |
| 9. Production packaging | Docker, env config, health checks, error handling (T025–T026) | Not started |
| 10. Deployment | Vercel + Render + Supabase + R2 + Gemini (T027–T028) | Not started |

## Sequencing discipline
- One task at a time; a phase's tasks are dependency-ordered within it.
- Do not start LangChain/LangGraph work (Phases 4–5) before the raw pipeline (Phases 1–3) is correct and tested — the whole point of building it framework-free first is to make the framework version explainable, not a shortcut.
- Do not start Phase 7 auth/backend work assuming a UI; do not start Phase 8 frontend work against unstable APIs.
- Phase 9–10 (Docker, deployment) come last, after the app is functionally complete — don't deploy a half-built pipeline.

## Companion documents
- `RAG_DESIGN.md` — chunking/embedding/retrieval design and the FAISS persistence strategy under Render's ephemeral storage
- `EVALUATION_PLAN.md` — Phase 6 evaluation approach
- `DEPLOYMENT.md` — Phase 9–10 infrastructure detail

## Current status
T001–T003 complete and verified. T004 — Chunking is the active task (Phase 1).
