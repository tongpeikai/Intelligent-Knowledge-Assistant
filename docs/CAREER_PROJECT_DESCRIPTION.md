# Career Project Description

## Formal resume entry

**Intelligent Knowledge Assistant | AI Application Engineering Project**

Built an offline-first knowledge assistant with a hand-written multi-step Agent loop, OpenAI-compatible Function Calling, local BGE embeddings, persistent ChromaDB RAG, SQLite session memory, FastAPI and Gradio. Implemented secure PDF/TXT/Markdown ingestion, incremental indexing, source/page tracing, controlled tool execution, retries, timeouts, repeated-call protection and Mock-mode end-to-end testing. Created a reproducible weak-label retrieval benchmark and improved English queries over a Chinese corpus from 0.857 to 1.000 Recall@3/Precision@3/MRR on the disclosed 8-case project set using dependency-free bilingual term expansion.

## Technology stack

Python 3.10 · OpenAI SDK / DeepSeek-compatible API · BGE-small-zh-v1.5 · Sentence Transformers · ChromaDB · SQLite · FastAPI · Pydantic · Gradio · pytest

## Core work completed

- Designed the module boundaries and shared service layer used by CLI, FastAPI and Gradio.
- Implemented Agent message/tool-call orchestration and the full `assistant tool_calls → role=tool result → final answer` loop.
- Added tool contracts, JSON/type validation, controlled retries, timeouts, trace records, repeated-call detection and dangerous-operation rejection.
- Extended RAG parsing to PDF/TXT/Markdown with chunk metadata, PDF page numbers, file hashes, incremental updates, duplicate detection and source deletion.
- Kept the existing 72-vector corpus intact and prevented public engineering documents from being accidentally indexed through an allowlist.
- Added SQLite session recovery, clear/delete operations, context compression and isolation tests.
- Built hardened local API endpoints and a demonstrable Gradio UI without adding external infrastructure.
- Established a baseline/optimized RAG evaluation script with explicit limitations instead of presenting a single unqualified score.

## Quantified evidence

- 57 automated tests pass, including Agent, RAG, Memory, API upload security and Gradio construction.
- 72 persistent Chroma chunks remain unchanged across evaluation and final verification.
- BGE model loads locally; FastAPI and Gradio both start on loopback and return HTTP 200.
- RAG weak-label set: 8 cases, 7 answerable and 1 no-answer; baseline and optimized metrics are recorded in `RAG_EVALUATION_REPORT.md`.
- Real paid LLM calls: 0; all automated verification uses Mock mode.

## Interview talking points

1. Explain why a tool call is a protocol round trip rather than a direct Python function invocation.
2. Explain how file hashes and metadata deletion make RAG updates incremental and non-duplicating.
3. Explain the trade-off of a deterministic bilingual glossary versus downloading a translation or reranking model.
4. Explain why document-level weak labels cannot prove production retrieval quality.
5. Explain how upload validation, optional Bearer auth and rate limiting protect a local demo without pretending to be a production identity system.

Detailed answers are in [`INTERVIEW_GUIDE.md`](INTERVIEW_GUIDE.md).
