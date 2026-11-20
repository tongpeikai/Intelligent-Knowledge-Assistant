"""Framework-independent application service used by CLI, API and Gradio."""

from pathlib import Path
from uuid import uuid4

from agent.llm_client import get_mode
from agent.loop import run_agent
from agent.memory import AgentSession
from agent.rag import index_document, search_documents
from agent.session_store import clear_session, delete_session, list_sessions


def new_session_id() -> str:
    return uuid4().hex


def chat(question: str, session_id: str | None = None) -> dict:
    sid = session_id or new_session_id()
    session = AgentSession.load_or_create(sid)
    result = run_agent(question, session=session)
    return {
        "session_id": sid,
        "mode": get_mode(),
        "answer": result.answer or "",
        "success": result.success,
        "steps": result.steps,
        "trace": [record.__dict__ for record in result.tool_calls],
        "aborted_reason": result.aborted_reason,
    }


def history(session_id: str) -> list[dict]:
    session = AgentSession.load_or_create(session_id)
    return [m for m in session.messages if m.get("role") in {"user", "assistant"}]


def upload(path: str, filename: str | None = None) -> dict:
    if filename:
        from agent.config import UPLOAD_DIR
        source = Path(path)
        target = UPLOAD_DIR / Path(filename).name
        if source != target:
            target.write_bytes(source.read_bytes())
        return index_document(target)
    return index_document(path)


def retrieve(query: str, top_k: int = 3, max_distance: float = 0.5) -> list[dict]:
    return search_documents(query, top_k=top_k, max_distance=max_distance)


__all__ = [
    "chat", "history", "upload", "retrieve", "new_session_id",
    "clear_session", "delete_session", "list_sessions",
]
