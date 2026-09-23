# DEPLOYMENT — SourceX

Locked deployment direction (see `PRD.md` §Deployment direction). Not re-litigated against alternatives during normal development.

## Target infrastructure

| Component | Service | Notes |
|---|---|---|
| Frontend | Vercel | Next.js, deployed from the same repo |
| Backend | Render Free | FastAPI, Dockerized (T025) |
| Database | Supabase (Postgres Free tier) | Users, document metadata, chunk metadata |
| Document storage | Cloudflare R2 | Original PDFs — never the backend's local filesystem |
| AI provider | Gemini API | Embeddings + generation; key server-side only |
| Vector retrieval | FAISS | See persistence strategy below |

## Ephemeral storage constraint (important)
Render Free's local disk does not persist across restarts/redeploys. This means:
- The FAISS index file cannot be relied on as permanent storage.
- Uploaded PDFs must go to R2, not the local filesystem.
- The FAISS index is rebuilt/reloaded from durably-stored embeddings (Postgres and/or R2) at startup or on first access — see `RAG_DESIGN.md` for the full rationale. This is a deliberate choice to avoid introducing a hosted vector database purely to work around a free-tier hosting quirk.

## Environment configuration
All of the following are environment variables, never hardcoded, never sent to the frontend:
- `GEMINI_API_KEY`
- Database connection string (Supabase)
- Cloudflare R2 credentials/bucket config
- Any auth secret/signing key (once T021 lands)

## Free-tier scope
Designed for portfolio visitors and interview demos — not guaranteed concurrency or enterprise uptime. Rate limiting, file-size limits, and graceful provider-failure handling (T026) are the actual reliability strategy, not infrastructure scale.

## Future scaling note
Cloud Run (or similar) may be discussed later purely as a scalability alternative if this ever needed to handle real traffic. It is explicitly not part of the current build — do not redesign around it now.

## Status
Not yet implemented — see `TASKS.md` T027 (deploy) and T025/T026 (Docker, error handling) as prerequisites.
