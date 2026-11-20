# Demo and Screenshot Guide

## Five-minute demonstration

1. Start Gradio in Mock mode and point out the visible mode badge.
2. Ask “RAG 是什么？” and show the `search_docs` tool trace and cited source.
3. Ask a follow-up in the same session to demonstrate context persistence.
4. Upload a fictional UTF-8 TXT or text PDF, build the knowledge base and query its content.
5. Start FastAPI and open `/docs`; demonstrate `/health`, `/chat` and `/rag/search`.
6. Run `pytest -q` and the RAG evaluation command.

## Public screenshot set

Store reviewed screenshots under `docs/assets/` using these names:

| File | Capture | Suggested caption |
|---|---|---|
| `gradio-chat.svg` | Mock badge, a RAG answer, source and tool trace (placeholder until screenshot capture) | Gradio multi-turn RAG chat in offline Mock mode |
| `agent-tool-trace.svg` | Expanded tool trace for a Function Calling turn (placeholder until screenshot capture) | Agent tool registration, execution and result return |
| `rag-sources.svg` | Retrieved chunks with source names and distances (placeholder until screenshot capture) | RAG retrieval results and source attribution |
| `memory-session.svg` | Two related turns in one fictional session (placeholder until screenshot capture) | SQLite-backed multi-turn memory |

Optional additional captures:

| `gradio-upload.png` | Fictional file upload and successful index count | Secure PDF/TXT/Markdown incremental ingestion |
| `fastapi-docs.png` | Local Swagger page with endpoint list | FastAPI interface for chat, sessions and knowledge management |
| `test-results.png` | Final pytest summary only | Automated Agent, RAG, Memory, API and UI verification |

Before capture, use a fresh fictional session and fictional document. Crop out browser profiles, local paths, terminal usernames, API tokens, private session IDs and unrelated windows. Screenshots are intentionally not generated automatically because final public images require a human privacy review.

## Commands

```powershell
$env:LLM_MODE='mock'
python -m app.gradio_app
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000
python -m pytest -q
python -m scripts.evaluate_rag
```
