# TASKS — SourceX

Status legend: `[ ]` not started · `[~]` in progress · `[x]` done

Tasks are scoped to one at a time (see `DEVELOPMENT_RULES.md`). Do not start the next task until the current one is verified.

## Phase 1 — RAG fundamentals (Day 1)

- [ ] T001 Repository foundation — project structure, dependency management (e.g. `pyproject.toml`/`requirements.txt`), environment config, `.gitignore`
- [ ] T002 PDF text extraction — extract raw text + page numbers from a sample PDF
- [ ] T003 Text cleaning — strip headers/footers/noise, normalize whitespace
- [ ] T004 Chunking — split cleaned text into overlapping chunks; document the chosen chunk size/overlap and why
- [ ] T005 Metadata — attach source file, page number, and chunk index to each chunk
- [ ] T006 Embeddings — generate embeddings for chunks using the chosen embedding model
- [ ] T007 FAISS indexing — build and persist a FAISS index from chunk embeddings
- [ ] T008 Retrieval — embed a query and retrieve nearest chunks from the FAISS index
- [ ] T009 Basic RAG generation — assemble retrieved context, call Gemini, produce a grounded answer

## Phase 2 — LangChain (Day 2, part 1)

- [ ] T010 LangChain pipeline — rebuild T002–T009 using LangChain loaders/splitters/embeddings/vector store/chain

## Phase 3 — LangGraph (Day 2, part 2)

- [ ] T011 LangGraph state definition
- [ ] T012 Analyze Query node
- [ ] T013 Retrieve node
- [ ] T014 Grade Evidence node + conditional edge
- [ ] T015 Rewrite Query node + retry loop
- [ ] T016 Generate node
- [ ] T017 Verify Sources node

## Phase 4+ (Day 3 and beyond)

- [ ] T018 Multi-document support
- [ ] T019 Citations (source file + page)
- [ ] T020 Conversational context
- [ ] T021 Tool calling (limited set)
- [ ] T022 Evaluation harness (retrieval + generation metrics)
- [ ] T023 FastAPI endpoints
- [ ] T024 Next.js UI
- [ ] T025 Docker setup
- [ ] T026 Tests
- [ ] T027 README + demo materials
- [ ] T028 Interview prep notes for this phase's concepts

## Notes
- Update this file's status as tasks complete — it's the live tracker, not a plan snapshot.
- Add new tasks here as they're identified; don't let scope live only in chat.
