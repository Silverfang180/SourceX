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
- **T004 Chunking:** 
  - *What it is:* A chunk is a subset of a document's text used as a discreet unit for embedding and retrieval. 
  - *Why it's needed:* A full page or document often exceeds LLM context windows and dilutes the embedding vector with too many unrelated concepts. Chunking narrows the focus to specific passages. 
  - *Why page != chunk:* A page is a physical layout artifact, not a logical one. A single page might contain multiple distinct topics that need separate retrieval scores.
  - *Approach/Trade-offs:* Chose a basic character-based window (1000 chars, 200 overlap). This is a simple baseline, not semantic chunking. It is computationally cheap and produces deterministic output while preserving page attribution. However, hard character boundaries can split words/sentences in half. Overlap is required so boundaries don't orphan critical context.
- **T005 Metadata:**
  - *What it is:* A formalized schema (using Python's `@dataclass`) that travels with each chunk of text through the entire pipeline. It provides a structured dataclass with type annotations and predictable attribute access (it does not perform runtime type validation).
  - *Why it's needed:* Once a document is shattered into thousands of chunks and embedded in a vector database, it becomes a soup of disconnected strings. Metadata is the only way to re-attach a retrieved chunk to its original document and page to generate a citation.
  - *Final Schema:* 
    * `text` — chunk content
    * `document_id` — stable document identifier
    * `source_file` — original source filename
    * `page_number` — 1-indexed human-readable page
    * `chunk_index` — deterministic chunk position
    This is what rides through to the final LLM prompt for citations.
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
