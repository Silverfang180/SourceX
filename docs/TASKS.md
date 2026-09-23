# TASKS — SourceX

Status: `[ ]` not started · `[~]` in progress · `[x]` done. One task at a time; don't start the next until the current one's acceptance criteria and tests pass. Every task follows the standard: Objective, Dependencies, Files/components, Acceptance criteria, Tests required, Definition of Done.

---

## Phase 1 — Document pipeline

### [x] T001 Repository foundation
- **Objective:** Establish project structure and config plumbing.
- **Dependencies:** None.
- **Files:** `src/sourcex/config.py`, `src/sourcex/__init__.py`, `tests/__init__.py`, `tests/test_config.py`, `requirements.txt`, `.gitignore`.
- **Acceptance criteria:** `Config` singleton loads env vars via `python-dotenv`; imports resolve via `src` layout.
- **Tests:** `tests/test_config.py` passes.
- **DoD:** Verified via `pytest` — done, 1 passed.

### [x] T002 PDF text extraction
- **Objective:** Extract raw text + page numbers from a PDF.
- **Dependencies:** T001.
- **Files:** `src/sourcex/ingestion/extract.py` (or equivalent — confirm actual path against repo).
- **Acceptance criteria:** Given a sample PDF, returns per-page `{text, page_number, source_file}`.
- **Tests:** Extraction on a known sample PDF produces non-empty text and correct page count.
- **DoD:** Complete and verified.

### [x] T003 Text cleaning
- **Objective:** Strip noise (headers/footers, broken whitespace) from extracted text.
- **Dependencies:** T002.
- **Files:** cleaning module (confirm actual path against repo).
- **Acceptance criteria:** Cleaned output has normalized whitespace and reduced repeated header/footer noise, without losing real content.
- **Tests:** Unit tests on sample noisy text confirming expected cleanup.
- **DoD:** Complete and verified.

### [ ] T004 Chunking — **next**
- **Objective:** Split cleaned per-page text into overlapping chunks suitable for embedding/retrieval.
- **Dependencies:** T003.
- **Files:** `src/sourcex/ingestion/chunking.py`, `tests/test_chunking.py`.
- **Acceptance criteria:** Given cleaned page text, produces a list of chunk records `{text, page_number, chunk_index}`; chunk size and overlap are named constants with a documented rationale (in code comment or `RAG_DESIGN.md`); no chunk silently drops page attribution.
- **Tests:** Chunk count is sane for a known input length; overlap between consecutive chunks is verified; page number is preserved per chunk.
- **DoD:** Tests pass; chunk size/overlap choice documented in `RAG_DESIGN.md`.

### [ ] T005 Metadata
- **Objective:** Formalize the metadata schema attached to each chunk.
- **Dependencies:** T004.
- **Files:** metadata schema/dataclass, updated chunking output.
- **Acceptance criteria:** Every chunk carries `source_file`, `page_number`, `chunk_index`, and a stable `document_id`.
- **Tests:** Metadata fields present and correctly populated on sample data.
- **DoD:** Tests pass; schema documented in `RAG_DESIGN.md`.

## Phase 2 — Retrieval foundation

### [ ] T006 Embeddings
- **Objective:** Generate embeddings for chunks via the Gemini embedding API.
- **Dependencies:** T005.
- **Files:** `src/sourcex/retrieval/embeddings.py`.
- **Acceptance criteria:** Given chunk text, returns a vector of the expected dimensionality; API key read from `Config`, never hardcoded.
- **Tests:** Mocked API test confirming call shape and output handling; graceful handling of an API error/rate limit.
- **DoD:** Tests pass; failure handling documented.

### [ ] T007 FAISS indexing
- **Objective:** Build and persist a FAISS index from chunk embeddings.
- **Dependencies:** T006.
- **Files:** `src/sourcex/retrieval/index.py`.
- **Acceptance criteria:** Index builds from a set of embeddings; can be saved and reloaded; persistence strategy matches `RAG_DESIGN.md` (not assuming permanent local disk).
- **Tests:** Round-trip test: build → save → load → search returns expected nearest neighbor on synthetic vectors.
- **DoD:** Tests pass.

### [ ] T008 Retrieval
- **Objective:** Given a query, embed it and retrieve nearest chunks.
- **Dependencies:** T007.
- **Files:** `src/sourcex/retrieval/retriever.py`.
- **Acceptance criteria:** Returns top-K chunks with metadata and similarity scores.
- **Tests:** Known query against a small known index returns expected chunk(s).
- **DoD:** Tests pass.

## Phase 3 — Basic RAG

### [ ] T009 Basic RAG generation
- **Objective:** Assemble retrieved context into a prompt, call Gemini, return an answer.
- **Dependencies:** T008.
- **Files:** `src/sourcex/generation/rag.py`.
- **Acceptance criteria:** Given a question, returns an answer plus which chunks it was generated from; no framework used yet.
- **Tests:** Mocked LLM call test; integration test on a small sample document end-to-end (extraction → answer).
- **DoD:** Tests pass; this closes out the framework-free core (T001–T009).

## Phase 4 — LangChain

### [ ] T010 LangChain pipeline
- **Objective:** Rebuild T002–T009 using LangChain (loaders, splitters, embeddings wrapper, vector store, chain) as the pipeline genuinely used going forward.
- **Dependencies:** T009.
- **Files:** `src/sourcex/langchain_pipeline/`.
- **Acceptance criteria:** Produces equivalent results to the framework-free version; each LangChain component is mapped in `LEARNING_NOTES.md` to the manual step it replaces.
- **Tests:** Parity test against T009 output on the same sample document.
- **DoD:** Tests pass; framework-free version kept for reference, not deleted.

## Phase 5 — LangGraph

### [ ] T011 LangGraph state & skeleton
- **Objective:** Define the shared state object and graph skeleton (nodes/edges, no logic yet beyond passthrough).
- **Dependencies:** T010.
- **Files:** `src/sourcex/graph/state.py`, `src/sourcex/graph/graph.py`.
- **Acceptance criteria:** Graph compiles and runs start-to-end with stub nodes.
- **Tests:** Graph executes without error on a sample input.
- **DoD:** Tests pass.

### [ ] T012 analyze_query + retrieve_context nodes
- **Objective:** Implement query analysis and retrieval as real graph nodes using T010's LangChain retriever.
- **Dependencies:** T011.
- **Files:** graph nodes.
- **Acceptance criteria:** State after these nodes contains retrieved chunks.
- **Tests:** Node-level test with a known query.
- **DoD:** Tests pass.

### [ ] T013 grade_context node + conditional edge
- **Objective:** Grade retrieved evidence as sufficient/insufficient; route accordingly.
- **Dependencies:** T012.
- **Files:** grading node + conditional edge logic.
- **Acceptance criteria:** Conditional routing genuinely branches based on grade, not a fixed path.
- **Tests:** Test both branches (sufficient and insufficient evidence cases).
- **DoD:** Tests pass.

### [ ] T014 rewrite_query node + retry loop
- **Objective:** On insufficient evidence, rewrite the query and loop back to retrieval.
- **Dependencies:** T013.
- **Files:** rewrite node, loop wiring, retry-limit guard.
- **Acceptance criteria:** Loop terminates (retry cap) even if evidence never becomes sufficient.
- **Tests:** Forced-insufficient case confirms rewrite + retry + eventual termination.
- **DoD:** Tests pass.

### [ ] T015 generate_answer node
- **Objective:** Generate the grounded answer once evidence is sufficient.
- **Dependencies:** T013.
- **Files:** generation node.
- **Acceptance criteria:** Answer includes source chunk references.
- **Tests:** Node-level test.
- **DoD:** Tests pass.

### [ ] T016 verify_citations node
- **Objective:** Verify generated claims are supported by cited chunks; flag unsupported claims instead of silently passing them through.
- **Dependencies:** T015.
- **Files:** verification node.
- **Acceptance criteria:** Detects at least an obvious unsupported-claim case in a test fixture.
- **Tests:** Supported vs. unsupported claim test cases.
- **DoD:** Tests pass; this completes the full LangGraph workflow (T011–T016).

### [ ] T017 Tool calling (where appropriate)
- **Objective:** Add a small, deliberate toolset (e.g. calculator, document search/lookup) into the graph.
- **Dependencies:** T016.
- **Files:** tool definitions + node wiring.
- **Acceptance criteria:** At least one tool is genuinely invoked by the graph under a realistic query, not just defined and unused.
- **Tests:** Test triggering tool use.
- **DoD:** Tests pass.

## Phase 6 — Evaluation

### [ ] T018 Evaluation harness
- **Objective:** Build a small, defensible evaluation setup per `EVALUATION_PLAN.md`.
- **Dependencies:** T017.
- **Files:** `src/sourcex/evaluation/`, small labeled eval set.
- **Acceptance criteria:** Produces retrieval and generation metrics (see `EVALUATION_PLAN.md`) runnable as a script/test.
- **Tests:** Harness runs end-to-end on the eval set and outputs numbers.
- **DoD:** Tests pass; results documented in `LEARNING_NOTES.md`.

## Phase 7 — Backend/application

### [ ] T019 FastAPI application skeleton
- **Objective:** Expose upload/query endpoints wrapping the LangGraph pipeline.
- **Dependencies:** T018.
- **Files:** `src/sourcex/api/`.
- **Acceptance criteria:** `/upload` and `/query` endpoints work locally against the existing pipeline; health endpoint present.
- **Tests:** API integration tests (e.g. via `TestClient`).
- **DoD:** Tests pass.

### [ ] T020 PostgreSQL integration (Supabase)
- **Objective:** Persist users, document metadata, and chunk metadata.
- **Dependencies:** T019.
- **Files:** DB models/migrations, connection config via `Config`.
- **Acceptance criteria:** Schema covers users, documents, chunks; connects to Supabase via env-configured URL.
- **Tests:** DB integration tests against a test database/schema.
- **DoD:** Tests pass.

### [ ] T021 Authentication
- **Objective:** User signup/login.
- **Dependencies:** T020.
- **Files:** auth module/endpoints.
- **Acceptance criteria:** Users can sign up and log in; sessions/tokens issued securely.
- **Tests:** Auth flow integration tests.
- **DoD:** Tests pass.

### [ ] T022 User/document isolation
- **Objective:** Enforce `authenticated_user_id` + `requested_document_id` ownership check on every protected operation.
- **Dependencies:** T021.
- **Files:** authorization middleware/dependency, applied across upload/query/delete/download endpoints.
- **Acceptance criteria:** A user cannot access another user's document by ID manipulation — verified directly.
- **Tests:** Negative test: user A cannot read/query/delete user B's document.
- **DoD:** Tests pass — this is a security-critical task; no partial credit.

### [ ] T023 Document storage integration
- **Objective:** Store PDFs in Cloudflare R2; finalize FAISS persistence strategy per `RAG_DESIGN.md` (index rebuilt/loaded, not assumed permanent on local disk).
- **Dependencies:** T020.
- **Files:** storage client, index load/rebuild logic tied to app startup or first-query.
- **Acceptance criteria:** Upload writes to R2, not local disk; FAISS index survives a simulated container restart (rebuilt from persisted embeddings/metadata).
- **Tests:** Integration test simulating restart and confirming retrieval still works.
- **DoD:** Tests pass.

## Phase 8 — Frontend

### [ ] T024 Next.js frontend
- **Objective:** Upload, processing status, query, citations display, document management UI.
- **Dependencies:** T019, T021.
- **Files:** Next.js app.
- **Acceptance criteria:** A user can complete the full flow (upload → ask → see grounded answer with citations) through the UI.
- **Tests:** Basic component/e2e smoke test.
- **DoD:** Manually verified end-to-end + smoke test passing.

## Phase 9 — Production packaging

### [ ] T025 Docker
- **Objective:** Containerize the FastAPI backend.
- **Dependencies:** T023.
- **Files:** `Dockerfile`, `.dockerignore`.
- **Acceptance criteria:** Image builds and runs locally, serving the same API.
- **Tests:** Container smoke test (health endpoint responds).
- **DoD:** Verified locally.

### [ ] T026 Error handling & health checks
- **Objective:** Graceful handling of AI-provider failures/rate limits, file-size limits, validation errors; health endpoint.
- **Dependencies:** T019.
- **Files:** error-handling middleware, `/health` endpoint.
- **Acceptance criteria:** Simulated provider failure returns a clean error, not a crash; oversized file rejected with a clear message.
- **Tests:** Fault-injection tests for provider failure and oversized upload.
- **DoD:** Tests pass.

## Phase 10 — Deployment

### [ ] T027 Deploy
- **Objective:** Deploy frontend to Vercel, backend (Docker) to Render Free, DB to Supabase, storage to R2.
- **Dependencies:** T024, T025, T026, T023.
- **Files:** deployment configs/env var setup docs in `DEPLOYMENT.md`.
- **Acceptance criteria:** Live URL serves the full working flow.
- **Tests:** Manual end-to-end verification against the live deployment.
- **DoD:** Live and verified.

### [ ] T028 Final testing/review
- **Objective:** End-to-end review against `PRD.md` §Success criteria.
- **Dependencies:** T027.
- **Files:** README update, portfolio description.
- **Acceptance criteria:** Every item in the PRD success-criteria list is genuinely true of the deployed app; README makes no unimplemented claims.
- **Tests:** Full manual walkthrough of the deployed app.
- **DoD:** Signed off against `PRD.md`.

---

## Notes
- Don't unnecessarily modify T001–T003 absent a real defect.
- Keep this file's status current — it's the live tracker Antigravity reads, not a snapshot.
