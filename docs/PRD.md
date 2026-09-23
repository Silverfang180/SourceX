# PRD — SourceX

## Product Name
**SourceX** — *Source Exploration & Reasoning*

## One-line description
SourceX is an agentic document intelligence platform that retrieves evidence from user-provided documents and uses that evidence to produce traceable, source-grounded answers with page-level citations.

## Sequencing (locked)
**Build the complete project → Deploy it → Update resume/portfolio → Deeply learn the complete system.**

Implementation is not blocked on first mastering RAG/LangChain/LangGraph theory. Only the minimum explanation needed for the current task is given during the build; deeper theory is recorded in `LEARNING_NOTES.md`, which becomes the deep-learning curriculum once the system is deployed. The completed, deployed project is itself the learning artifact.

## Final MVP scope
A user can:
1. Create/authenticate an account
2. Upload a reasonable-sized PDF
3. Have it processed: extract → clean → chunk → embed → index
4. Ask questions about the document
5. Get an answer from a **genuinely integrated** LangChain retrieval/generation pipeline
6. Orchestrated by a **genuinely integrated** LangGraph workflow (query analysis, retrieval, context grading, query rewriting on poor retrieval, generation, citation verification)
7. See page-level source citations
8. Get graceful error handling throughout

Retrieval for a given user only draws from documents that user owns. Cross-document comparison/questioning may be included if practical, but must not delay the core MVP.

LangChain and LangGraph must be real parts of the working runtime — not installed-but-unused libraries.

## Non-goals
Kubernetes, microservices, distributed systems, GPU infrastructure, large local models, multiple vector databases, multiple LLM providers, complex agent swarms, excessive tool collections, elaborate enterprise observability, unnecessary cloud services. No claims of unlimited users, guaranteed high concurrency, or enterprise-grade availability/security.

## Deployment direction (locked)
- **Frontend:** Next.js → Vercel
- **Backend:** FastAPI + Docker → Render Free
- **Database:** PostgreSQL → Supabase Free
- **Document storage:** Cloudflare R2
- **AI:** Gemini API (embeddings + generation)
- **Vector retrieval:** FAISS

Not re-litigated against Cloud Run/Kubernetes/etc. during normal development — see `docs/DEPLOYMENT.md` for the full deployment design, including how FAISS's ephemeral-storage problem on Render is handled.

## Free-tier philosophy
Built for portfolio visitors and interview demonstrations, not enterprise scale: small numbers of concurrent users, reasonable PDF sizes, graceful failures, sensible rate limiting, useful loading/processing states. Credible engineering, not an enterprise SaaS pitch.

## Security requirements
Once auth exists, every protected operation (PDFs, metadata, chunks, retrieval results, generated results, deletion, downloads) must verify `authenticated_user_id` owns the `requested_document_id`, enforced server-side. Never trust a document ID alone. Secrets stay server-side, configured via environment variables.

## Success criteria — project completion
SourceX is complete when: the full document-to-answer RAG flow works; LangChain is genuinely integrated; LangGraph is genuinely integrated; citations are returned; retrieval can be evaluated; users/documents are isolated; the backend exposes usable APIs; the frontend provides a usable demo; the app is containerized and deployed; deployment failures are handled reasonably; and the README/portfolio description accurately reflects what's actually implemented — never claiming capability that doesn't exist.

## Current status
T001 (repository foundation), T002 (PDF extraction), T003 (text cleaning) complete and verified. T004 (chunking) is next. See `IMPLEMENTATION_PLAN.md` for the full phase breakdown and `TASKS.md` for the task-by-task handoff.
