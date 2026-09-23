# EVALUATION PLAN — SourceX

A small, defensible evaluation setup (Phase 6 / T018) — not an academic benchmark suite. The goal is metrics you can explain and justify in an interview, computed on a small dataset you build yourself.

## Evaluation dataset
- A small set of sample PDFs (a handful, covering at least one multi-page and one multi-column document) with a hand-written set of question → expected-answer-source pairs (which page/chunk should ground the answer).
- Size target: small enough to build and maintain by hand (roughly 10–30 question/answer pairs) — this is a portfolio-scale eval, not a research benchmark.

## Metrics

**Retrieval quality**
- **Recall@K** — does the correct source chunk appear in the top-K retrieved results, for the K actually used in production retrieval.
- **MRR (Mean Reciprocal Rank)** — only where it adds signal beyond Recall@K (e.g. if ranking position among retrieved chunks matters for the use case); skip if it doesn't add explainable value.

**Generation quality**
- **Answer relevance** — does the generated answer actually address the question (can be a simple LLM-graded or rule-based check on the small eval set; document whichever is used).
- **Faithfulness/groundedness** — does the answer's content actually appear in / follow from the retrieved chunks (ties directly to T016's citation verification logic — reuse it here rather than building a second mechanism).
- **Citation correctness** — does the cited page/chunk actually contain the claimed evidence.

**Operational**
- **Latency** — end-to-end time from question to answer, measured on the eval set.
- **Token usage / cost** — approximate per-query token count and resulting cost, using Gemini's published pricing, to demonstrate cost-awareness (not for billing purposes).

## What this is not
Not a claim of statistical significance, not a large labeled corpus, not a comparison against published RAG benchmarks. It's a repeatable, small, honest measurement of SourceX's own behavior — enough to say concretely "retrieval hits the right chunk N% of the time on my eval set" in an interview, rather than "it seems to work."

## Status
Not yet implemented — see `TASKS.md` T018. This document will be updated with actual numbers once T018 runs.
