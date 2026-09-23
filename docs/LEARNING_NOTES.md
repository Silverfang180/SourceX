# LEARNING NOTES — SourceX

This file is the **future deep-learning curriculum** (per `DEVELOPMENT_RULES.md`: build first, learn deeply once the system is complete and deployed). Two kinds of entries:

- **Working notes** — minimum understanding captured while implementing.
- **Deferred deep-dives** — flagged for the structured post-deployment learning pass.

Entry format once expanded: (1) what it is, (2) why SourceX needs it, (3) how the implementation works, (4) key terminology, (5) trade-offs, (6) limitations, (7) likely interview questions.

## T002 — PDF text extraction (working notes)
- PDF = page-description format, no guaranteed linear reading order; PyMuPDF (`fitz`) reconstructs approximate order from positioned glyphs.
- Extraction captures `{text, page_number, source_file}` per page — page number captured here because it's the seed of every later citation.
- Known failure modes: multi-column scrambling, hyphenation breaks, header/footer noise, font-encoding garbling, table structure loss, scanned/image-only PDFs returning nothing (OCR out of scope for MVP).
- **Deferred:** OCR fallback design, position-aware extraction for tables, alternatives to PyMuPDF (pdfplumber, pdfminer) and trade-offs.

## T003 — Text cleaning
- **Deferred:** working notes pending — task complete and verified, write-up not yet captured.

## Upcoming working notes (fill in as each task lands)
- T004 Chunking — chunk size/overlap choice and why
- T005 Metadata — final schema and what rides through to citations
- T006–T009 — embeddings, FAISS, retrieval, basic generation mechanics
- T010 — LangChain component-by-component mapping to the manual T001–T009 steps
- T011–T017 — LangGraph state/nodes/conditional edges/loop termination, tool calling
- T018 — evaluation results and what they show
- T019–T023 — API design, auth model, user isolation enforcement, FAISS rebuild-on-restart mechanics
- T024–T028 — frontend architecture, Docker, deployment specifics

## Interview question bank (living list, answer from actual implementation)
- Why can't a PDF be read like a `.txt` file? What conceptual understanding is needed beyond "PyMuPDF does it for me"?
- Why is page number captured at extraction time, not reconstructed later?
- Why FAISS, why embeddings, how does retrieval work, why was chunk size chosen the way it was?
- What happens when retrieval fails, and how does query rewriting address it?
- Why LangChain, why LangGraph, why is LangGraph suited to conditional workflows specifically?
- How are citations generated and verified — what would a false-but-plausible citation look like, and how is it caught?
- How was the RAG system evaluated, and what do the numbers actually show?
- How is FAISS's index kept usable given Render's ephemeral storage — what's the actual rebuild mechanism?
- How is user/document isolation enforced, and how would you demonstrate it's actually secure (not just present)?
- What are the system's real limitations, stated honestly?
