# Project Showcase

## What this project demonstrates

Intelligent Knowledge Assistant is an offline-first AI application engineering project. It implements the control plane around an LLM instead of hiding it behind a large orchestration framework: structured tool calling, validation, controlled execution, RAG, persistent memory, observable traces, API security and an interactive UI.

## Technology map

| Technology | Where it is used | Engineering value |
|---|---|---|
| Python 3.10 | Whole project | Typed, modular application code |
| OpenAI SDK / DeepSeek-compatible API | `agent/llm_client.py` | Mock/API switch, timeout and retry |
| Hand-written Agent loop | `agent/loop.py` | Transparent multi-tool execution |
| JSON Schema tool definitions | `agent/tools.py` | Function Calling contracts and validation |
| BGE-small-zh-v1.5 | `agent/rag.py` | Local Chinese 512-dimensional embeddings |
| ChromaDB | `agent/rag.py` | Persistent cosine retrieval and metadata filters |
| SQLite | `session_store.py`, `tools.py` | Session history and small structured data |
| FastAPI / Pydantic | `app/api.py` | Validated API, upload security, auth and limits |
| Gradio | `app/gradio_app.py` | Local chat, upload and trace demonstration |
| pytest | `tests/` | Unit, integration, security and workflow coverage |

## Key engineering problems solved

1. **Safe offline development:** Mock is the default and clearly labeled, so the entire Agent workflow can be tested without balance or paid calls.
2. **Reliable tool loop:** Tool arguments are parsed and validated; failures, timeouts, repeated calls and dangerous names become controlled tool results rather than process crashes.
3. **Non-destructive incremental RAG:** File hashes prevent duplicate indexing; updates replace only the affected source; deletion uses metadata filters; the original 72-vector corpus is preserved.
4. **Public docs versus knowledge data:** A strict allowlist prevents engineering documentation from accidentally entering the vector corpus, while uploads remain in Git-ignored storage.
5. **English against Chinese corpus:** A small deterministic bilingual glossary improves known technical English queries without a new model or online translation service. The report retains baseline and optimized metrics.
6. **Persistent multi-session memory:** Sessions are isolated in SQLite and can be restored, cleared or summarized without mixing users.
7. **Secure local API boundary:** Upload size/content/path checks, sanitized errors, local CORS, optional Bearer auth and rate limiting are implemented without external infrastructure.

## Measured results

- Automated tests: see the latest `pytest` result in the acceptance report; tests cover Agent, RAG, Memory, API and Gradio.
- Vector corpus: 72 chunks across three public sample documents.
- Fixed weak-label RAG set: baseline Recall@3 / Precision@3 / MRR = 0.857 / 0.857 / 0.857; optimized = 1.000 / 1.000 / 1.000.
- These RAG numbers describe only 8 project-local document-level labels and must not be presented as production accuracy.

## Resume-ready description

**Intelligent Knowledge Assistant — AI Application Engineering Project**

- Built an offline-first knowledge assistant with a hand-written multi-step Agent loop, OpenAI-compatible Function Calling, deterministic Mock LLM testing and optional DeepSeek integration.
- Implemented local RAG with BGE-small-zh-v1.5 and persistent ChromaDB, supporting PDF/TXT/Markdown parsing, page/source metadata, incremental updates, duplicate detection, deletion and distance-filtered Top-K retrieval.
- Designed SQLite-backed multi-session memory with history recovery and rolling summarization; exposed the system through a hardened FastAPI API and a Gradio chat/upload interface.
- Added controlled tool execution with schema validation, retries, timeouts, repeated-call protection, dangerous-operation blocking and observable traces; established automated Agent/RAG/API/UI tests.
- Created a reproducible weak-label RAG evaluation pipeline and improved English retrieval over a Chinese corpus from 0.857 to 1.000 Recall@3/MRR on the 8-case project test set using dependency-free bilingual term expansion.

Use the metrics sentence only together with the small-test-set qualification.
