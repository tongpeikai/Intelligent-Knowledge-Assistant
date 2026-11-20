"""Hardened local FastAPI interface for the Intelligent Knowledge Assistant."""

import hmac
import os
import time
from collections import defaultdict, deque
from pathlib import Path
from threading import Lock
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from agent.config import MAX_UPLOAD_BYTES, UPLOAD_DIR
from agent.llm_client import get_mode
from agent.rag import SUPPORTED_SUFFIXES, list_documents
from app import service
from logging_config import setup_logging

setup_logging(console=False)
app = FastAPI(title="Intelligent Knowledge Assistant API", version="2.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:7860", "http://localhost:7860"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

_RATE_LIMIT = int(os.environ.get("API_RATE_LIMIT_PER_MINUTE", "60"))
_requests: dict[str, deque[float]] = defaultdict(deque)
_rate_lock = Lock()


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str | None = Field(default=None, max_length=128)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=50)
    max_distance: float = Field(default=0.5, ge=0, le=2)


def _authorized(request: Request) -> bool:
    expected = os.environ.get("IKA_API_TOKEN")
    if not expected:
        return True
    supplied = request.headers.get("Authorization", "")
    return supplied.startswith("Bearer ") and hmac.compare_digest(supplied[7:], expected)


@app.middleware("http")
async def local_security(request: Request, call_next):
    if request.url.path not in {"/health", "/docs", "/openapi.json", "/redoc"}:
        if not _authorized(request):
            return JSONResponse(status_code=401, content={"error": "unauthorized"})
        client = request.client.host if request.client else "local"
        now = time.monotonic()
        with _rate_lock:
            bucket = _requests[client]
            while bucket and bucket[0] <= now - 60:
                bucket.popleft()
            if len(bucket) >= _RATE_LIMIT:
                return JSONResponse(status_code=429, content={"error": "rate_limit_exceeded"})
            bucket.append(now)
    return await call_next(request)


@app.exception_handler(Exception)
async def unhandled_error(_, exc: Exception):
    # Full details stay in local logs; clients receive no paths, secrets or internals.
    import logging
    logging.getLogger("api").exception("Unhandled API error", exc_info=exc)
    return JSONResponse(status_code=500, content={"error": "internal_error", "detail": "服务器内部错误"})


def _validate_content(filename: str, data: bytes) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        if not data.startswith(b"%PDF-"):
            raise HTTPException(status_code=415, detail="文件扩展名与 PDF 内容不匹配")
        return
    if b"\x00" in data:
        raise HTTPException(status_code=415, detail="文本文件包含二进制内容")
    try:
        data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=415, detail="文本文件必须使用 UTF-8 编码") from exc


@app.get("/health")
def health():
    return {"status": "ok", "mode": get_mode(), "api_calls_enabled": get_mode() == "api"}


@app.post("/chat")
def chat(req: ChatRequest):
    result = service.chat(req.question, req.session_id)
    if not result["success"]:
        raise HTTPException(status_code=502, detail="模型任务未能完成")
    return result


@app.get("/sessions")
def sessions():
    return service.list_sessions()


@app.get("/sessions/{session_id}")
def session_history(session_id: str):
    return {"session_id": session_id, "messages": service.history(session_id)}


@app.post("/sessions")
def create_session():
    return {"session_id": service.new_session_id()}


@app.delete("/sessions/{session_id}")
def remove_session(session_id: str):
    service.delete_session(session_id)
    return {"deleted": True, "session_id": session_id}


@app.post("/sessions/{session_id}/clear")
def reset_session(session_id: str):
    service.clear_session(session_id)
    return {"cleared": True, "session_id": session_id}


@app.post("/rag/search")
def rag_search(req: SearchRequest):
    return {"query": req.query, "results": service.retrieve(req.query, req.top_k, req.max_distance)}


@app.get("/knowledge/documents")
def knowledge_documents():
    return list_documents()


@app.get("/tools")
def tool_definitions():
    from agent.tools import tools
    return tools


@app.post("/knowledge/upload")
async def upload_document(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name
    if not filename or filename != (file.filename or ""):
        raise HTTPException(status_code=400, detail="非法文件名")
    if Path(filename).suffix.lower() not in SUPPORTED_SUFFIXES:
        raise HTTPException(status_code=415, detail="仅支持 PDF、TXT、Markdown 文件")

    data = bytearray()
    while chunk := await file.read(64 * 1024):
        data.extend(chunk)
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=f"文件不能超过 {MAX_UPLOAD_BYTES // 1024 // 1024} MB")
    _validate_content(filename, bytes(data))

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = UPLOAD_DIR / f".{uuid4().hex}-{filename}"
    try:
        temp_path.write_bytes(data)
        return service.upload(str(temp_path), filename=filename)
    finally:
        temp_path.unlink(missing_ok=True)
