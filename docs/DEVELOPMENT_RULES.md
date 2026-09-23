# DEVELOPMENT RULES — SourceX

## Sequencing (locked)
**Build the complete project → Deploy it → Update resume/portfolio → Deeply learn the complete system.**

Implementation is never blocked on mastering theory first. Give only the minimum explanation needed for the current task; deeper material goes in `LEARNING_NOTES.md` for later. This changes pacing only — documentation honesty, review discipline, and scope control below are unchanged.

## Tool division
**Claude:** architecture, planning, technical decisions, documentation, learning notes, design review, code review, implementation guidance, spotting architectural problems, interview prep, scope alignment. Updates project documentation directly where possible.

**Antigravity:** reads repo docs, implements tasks from `TASKS.md`, writes code and tests, runs tests, debugs, updates task status, reports changes, stops after the assigned task.

## Workflow
```
Claude: architecture / task definition
  ↓
Repository documentation (source of truth)
  ↓
Antigravity: implementation → tests → TASKS.md update
  ↓
Claude: review / corrections / next task
  ↓ repeat
```
No two independent implementations, no conflicting architectures between Claude and Antigravity.

## One task at a time
Every task in `TASKS.md` is small, independently verifiable, and carries: objective, dependencies, files/components, acceptance criteria, required tests, and a definition of done. Never "build the entire RAG system" as a task. Don't unnecessarily modify a completed task unless a real defect is found — T001–T003 stand as-is.

## Scope control
Avoid unless genuinely required: Kubernetes, microservices, distributed systems, GPU infrastructure, multiple vector databases, multiple LLM providers, large local models, complex agent swarms, excessive tools, enterprise observability, unnecessary cloud services. Every addition needs a concrete technical reason. The project must stay explainable in an interview.

## Documentation honesty
Never document a feature as done if it isn't. Docs reflect actual repository state. Never claim a capability (e.g. "LangGraph integrated") that isn't genuinely wired into the runtime — installed-but-unused is not integrated.

## Review standard
Check: correctness, tests, maintainability, architecture consistency, security, unnecessary complexity, explainability, whether the task's acceptance criteria are actually met. Prefer simple-and-correct over impressive-and-complicated. On a problem: (1) explain the issue, (2) explain why it matters, (3) give a precise correction task.

## Security discipline
Every protected document operation verifies `authenticated_user_id` owns `requested_document_id`, server-side, before proceeding — never trust an ID alone. Secrets via environment variables only, never in code or sent to the frontend.

## Task tracking
`docs/TASKS.md`, organized into Phases 1–10, is the live handoff to Antigravity.
