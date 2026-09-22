# PRD — SourceX

## Product Name
**SourceX** — *Source Exploration & Reasoning*

## One-line description
SourceX is an agentic document intelligence platform that retrieves evidence from user-provided documents and uses that evidence to produce traceable, source-grounded answers.

## Problem
Most "chat with your PDF" demos hide their mechanics behind a framework and answer without verifiable grounding. They're easy to build shallow and hard to defend in an interview. There's no portfolio artifact that demonstrates, end-to-end, that the builder understands retrieval, evaluation, and agentic orchestration rather than having assembled a LangChain tutorial.

## Goal
Build a project that is simultaneously:
1. A working system — ingest documents, retrieve relevant evidence, generate grounded answers with citations.
2. A learning vehicle — every core mechanism (chunking, embeddings, retrieval, grading, routing) is understood well enough to explain and defend in an AI Engineer interview.
3. A defensible engineering artifact — evaluated, tested, documented, and reasoned about in terms of trade-offs, not just "it works."

## Non-goals (out of scope for MVP)
- Multi-agent swarm architectures
- Fine-tuning
- Voice interfaces
- Multiple LLM providers or multiple vector databases
- Kubernetes / complex microservices
- Elaborate authentication
- Dozens of tools

These are explicitly excluded to keep the 3-day MVP scope achievable and to keep the core (RAG correctness, source grounding, evaluation) strong rather than shallow-but-wide.

## Target outcome
A working local/dockerized application where a user can:
- Upload one or more documents (PDF)
- Ask a question
- Receive an answer that is grounded in retrieved evidence, with citations back to the source document/page
- See the system retry/rewrite the query when initial retrieval is weak (LangGraph routing)

Plus: a set of documented, understood evaluation metrics (retrieval quality, faithfulness, citation correctness) run against the system.

## Users
Primary user: the builder, evaluated by an interviewer. The product's real "user" is the interview conversation this project needs to support — every design decision should be explainable and defensible.

## Success criteria
- Core RAG pipeline (no framework) works and is understood at the mechanics level (Day 1)
- LangChain/LangGraph rebuild demonstrates the same functionality plus conditional retrieval correction (Day 2)
- Citations are traceable to real source locations, not hallucinated (Day 4 phase)
- At least retrieval quality (Recall@K) and faithfulness/groundedness are measured, not just assumed (Day 6 phase)
- The builder can answer the interview question bank in `LEARNING_NOTES.md` / future `INTERVIEW_PREP.md` using the actual implementation, not generic answers

## Constraints
- 2–3 day MVP build window (see `IMPLEMENTATION_PLAN.md` for the day-by-day breakdown; phases beyond Day 3 continue afterward as scope allows)
- Two-tool workflow: Claude (architecture/docs/review) and Google Antigravity (implementation), coordinating through the repository as source of truth
- Only one task implemented at a time — no jumping ahead to later phases before the current one is solid

## Current status
Project foundation stage. No application code yet. Establishing documentation and Day 1 plan before any implementation begins.
