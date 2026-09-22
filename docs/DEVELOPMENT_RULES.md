# DEVELOPMENT RULES — SourceX

## Tool division

**Claude** owns: architecture, project planning, documentation, technical decisions, learning explanations, implementation specifications, code review, debugging analysis, interview preparation, identifying architectural problems, maintaining project documentation.

**Google Antigravity** owns: implementing code, modifying repository files, writing tests, running tests, fixing implementation errors, updating task status, implementing only the currently assigned task.

Claude and Antigravity do not talk to each other directly — they communicate **through the SourceX repository**. The repository is the source of truth. Anything that matters must eventually live in `docs/` or in the code itself, not only in a chat transcript.

## One task at a time

Antigravity is never instructed to "build SourceX" or "build phase 3." It is given exactly one task from `TASKS.md`, scoped to specific files, with an explicit verification step. If a task can't be described that precisely, it's too big — split it.

## No hidden mechanics

If a framework provides a helper that collapses multiple steps (e.g. a `create_rag_chain()`-style call, or a LangGraph prebuilt), the underlying steps must still be understood and, ideally, documented in `LEARNING_NOTES.md`:
1. What it is
2. Why it is needed
3. How it works
4. Where it fits in SourceX
5. What alternatives exist
6. What trade-offs exist
7. How to explain it in an interview

## No scope creep

Don't add a technology, phase, or feature because it looks impressive on a resume. Every addition needs a concrete technical reason tied to the PRD. Kubernetes, multi-agent swarms, fine-tuning, multiple LLM providers/vector DBs, and similar are explicitly out of scope for the MVP — see `PRD.md`.

## Documentation honesty

Never document a feature as completed if it hasn't been implemented. Documentation should reflect the actual state of the repository, not the intended future state. Keep terminology consistent across documents.

## Review loop

After Antigravity completes a task, Claude reviews for:
- implementation correctness
- architecture fit
- tests
- maintainability
- security
- performance
- unnecessary complexity
- whether the concept is actually understood (not just working)

If something is wrong, the review must: (1) explain the issue, (2) explain why it matters, (3) produce a precise correction task for Antigravity.

## Focus discipline

Work stays scoped to the current phase/day. If the current work is PDF extraction, don't start designing the full LangGraph system. If the current work is embeddings, stay on embeddings. See `IMPLEMENTATION_PLAN.md` for what "current" means at any point.

## Task tracking

`docs/TASKS.md` is the live task list. Tasks are small and independently verifiable (e.g. `T001 Repository foundation`, `T002 PDF extraction`). Status is updated as work completes.
