# Interview Guide

## Two-minute project explanation

This project is a local-first intelligent knowledge assistant. The user enters through CLI, FastAPI or Gradio; a shared service restores the SQLite session and invokes a hand-written Agent loop. The LLM may return structured tool calls. The loop validates JSON arguments, executes only registered tools with timeout/retry protection, writes the tool result back to the conversation, and continues until it receives a final answer. The RAG tool parses local documents, generates BGE embeddings, retrieves from persistent ChromaDB and returns source/page/distance metadata. Mock mode is the default, so the full workflow is testable without paid API calls.

## Likely questions and reference answers

### Why not use LangChain?

The goal was to expose the essential orchestration mechanics. A small hand-written loop makes message roles, tool call IDs, validation, retries and termination conditions explicit. For a larger team, a framework could reduce boilerplate, but it would not remove the need for these safety boundaries.

### What makes this Function Calling rather than a normal Python function call?

The model receives JSON Schema tool definitions and returns structured `tool_calls`. The application parses the generated arguments, runs the selected tool, adds a `role=tool` message with the matching call ID, and asks the model to continue. Tests simulate this complete round trip, including multiple calls and failures.

### How do you prevent Agent loops?

There is a global step limit, total timeout and a signature made from tool name plus sorted arguments. Repeating the same signature beyond the configured limit does not execute the tool again; it sends corrective feedback to the model and records the event.

### How does incremental indexing work?

Each source has a content hash stored beside Chroma. Unchanged files are skipped. A changed source has only its old vectors deleted by metadata, then its new chunks are embedded. Removed sources are cleaned from the collection. Stable IDs are derived from source and chunk position.

### Why did English retrieval fail, and how was it improved?

The corpus and BGE model usage are primarily Chinese, so an English semantic sentence ranked Chroma content above the RAG article. A deterministic glossary appends Chinese equivalents for known technical terms before embedding. This needs no network or new model and fixed the labeled case, but it is intentionally disclosed as limited-domain expansion rather than general translation.

### How are RAG metrics calculated?

The fixture contains expected source documents. Recall@K checks whether every expected source appears, Precision@K counts relevant retrieved chunks over K, and MRR uses the first relevant rank. No-answer cases are excluded from those metrics and evaluated separately with the distance threshold. The labels are document-level and small, so results are not production claims.

### How is memory isolated?

Every session has an ID and a separate SQLite row containing summary and messages. Loading, clearing and deleting always use that ID. Tests create multiple sessions and verify that their content never crosses.

### What happens when a tool times out or fails?

Execution runs through a controlled wrapper. Timeout and retry exhaustion become text results returned to the Agent and error fields in the trace. The model can then recover or explain the failure instead of crashing the request.

### What protects file uploads?

The API enforces a byte limit, safe basename, allowlisted suffixes, PDF magic bytes, UTF-8 text and binary-content checks. Uploads stay in a Git-ignored directory. CORS is local-only, errors are sanitized, and optional Bearer auth and per-client rate limiting are available.

### Why is Gradio streaming not called native token streaming?

The current generator progressively renders the completed Agent answer. Tool execution must finish first. True first-token streaming would require an asynchronous event protocol across LLM tokens and tool lifecycle events; the documentation states this limitation rather than overstating it.

### What would you improve next?

First expand the anonymized labeled query set. Then add a lightweight lexical/BM25 channel and result diversification. For production, add an async event stream, reverse-proxy TLS, shared rate limiting, formal identity and structured observability.
