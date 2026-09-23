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
- **T006 Embeddings:**
  - *SDK Choice:* Upgraded to the modern `google-genai` SDK rather than the legacy `google-generativeai`.
  - *Model:* `gemini-embedding-2` with 768 dimensions. We encode chunks as "title: none | text: {chunk_text}" as required by the model.
  - *Architecture:* Created `src/sourcex/retrieval/embeddings.py` mapping `Chunk` to a new `EmbeddedChunk` dataclass. Used mocking in tests to prevent live API calls.
  - *Error Handling:* Caught raw `google.genai.errors.APIError` and wrapped it in a custom `EmbeddingError` so the rest of the application doesn't bleed SDK details.
- **T007 FAISS Indexing:**
  - *Vector Engine:* Implemented exact search using `faiss-cpu` and `IndexFlatIP`. Inner Product on normalized Gemini embeddings provides exact cosine-similarity ranking.
  - *ID Mapping:* Wrapped FAISS with `IndexIDMap` to link FAISS integer IDs to our unmodified `Chunk` metadata dictionaries.
  - *Persistence:* Created `.faiss` and `metadata.json` for local development serialization. Production architecture will rely on rebuilding this cache from durable Postgres/R2 storage because of ephemeral environments.
- **T008 Retrieval:**
  - *Query Format:* `gemini-embedding-2` requires specific task prefixes for queries. We format questions as `"task: question answering | query: {query}"` without sending a `task_type` parameter to the API config.
  - *Model Consistency:* Query inputs share the exact model (`gemini-embedding-2`) and dimensionality (`768`) as the document index, ensuring dimensional overlap.
  - *Retriever Class:* Created `src/sourcex/retrieval/retriever.py` to handle the transition from raw user question, to embedded vector, to nearest chunks retrieved from `VectorStore`.
- **T009 — Basic RAG Generation:**
  - *What it is:* A baseline pipeline that connects the `SearchResult` context from the FAISS retriever into an LLM prompt.
  - *Model:* Used `gemini-2.5-flash` for the generation step via the `google-genai` SDK.
  - *Architecture:* Developed a function `build_prompt` to string together retrieved chunks as contextual references `[Document 1]... [Document N]` with a question-answering template. `generate_answer` calls the Gemini model synchronously.
- **T010 — LangChain Pipeline:**
  - *What it is:* Transitioned the manual T002–T009 workflow to use native LangChain components.
  - *Mapping:*
    - **T002 (Extraction):** Hand-wrapped `PyMuPDFLoader` equivalent logic via `fitz` into `langchain_core.documents.Document` with metadata mapping.
    - **T003 (Cleaning):** Applied custom `clean_text` on chunk boundaries.
    - **T004/T005 (Chunking/Metadata):** Replaced manual iteration with `RecursiveCharacterTextSplitter`.
    - **T006 (Embeddings):** Transferred raw SDK logic to `GoogleGenerativeAIEmbeddings` from `langchain_google_genai`. Mapped the `title: none | text: {text}` schema via text mutation before embedding.
    - **T007 (FAISS):** `FAISS.from_documents` from `langchain_community.vectorstores` wraps FAISS indexing and metadata mapping out-of-the-box.
    - **T008/T009 (Retrieval/Generation):** `vectorstore.as_retriever()` + LCEL (LangChain Expression Language). Created a pipe `{"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | ChatGoogleGenerativeAI() | StrOutputParser()`.
  - *Why this way:* Proves the framework-free approach's primitives map cleanly onto standard enterprise orchestration without "magic." The result is equivalent to the manual implementation but allows standard interoperability.
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
