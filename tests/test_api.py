from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app, raise_server_exceptions=False)


def test_health_is_mock(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "mock")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["mode"] == "mock"


def test_chat_mock(monkeypatch, tmp_path):
    from agent import session_store
    monkeypatch.setattr(session_store, "SESSIONS_DB", tmp_path / "sessions.db")
    monkeypatch.setenv("LLM_MODE", "mock")
    response = client.post("/chat", json={"question": "你好", "session_id": "api-test"})
    assert response.status_code == 200
    assert response.json()["answer"].startswith("[Mock 模式]")


def test_chat_validation():
    response = client.post("/chat", json={"question": ""})
    assert response.status_code == 422


def test_upload_rejects_extension():
    response = client.post("/knowledge/upload", files={"file": ("bad.exe", b"x")})
    assert response.status_code == 415


def test_upload_rejects_path_traversal():
    response = client.post("/knowledge/upload", files={"file": ("../x.txt", b"safe")})
    assert response.status_code == 400


def test_upload_rejects_fake_pdf():
    response = client.post("/knowledge/upload", files={"file": ("x.pdf", b"not-pdf")})
    assert response.status_code == 415


def test_upload_size_limit(monkeypatch):
    monkeypatch.setattr("app.api.MAX_UPLOAD_BYTES", 3)
    response = client.post("/knowledge/upload", files={"file": ("x.txt", b"four")})
    assert response.status_code == 413


def test_optional_bearer_auth(monkeypatch):
    monkeypatch.setenv("IKA_API_TOKEN", "test-secret")
    assert client.get("/tools").status_code == 401
    assert client.get("/tools", headers={"Authorization": "Bearer test-secret"}).status_code == 200


def test_internal_error_is_sanitized(monkeypatch):
    monkeypatch.setattr("app.service.list_sessions", lambda: (_ for _ in ()).throw(RuntimeError("C:\\private\\secret")))
    response = client.get("/sessions")
    assert response.status_code == 500
    assert "private" not in response.text


def test_cors_allows_only_local_ui():
    response = client.options(
        "/chat",
        headers={"Origin": "http://127.0.0.1:7860", "Access-Control-Request-Method": "POST"},
    )
    assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:7860"


def test_rate_limit(monkeypatch):
    from app import api
    monkeypatch.setattr(api, "_RATE_LIMIT", 1)
    api._requests.clear()
    assert client.get("/tools").status_code == 200
    assert client.get("/tools").status_code == 429
    api._requests.clear()


def test_valid_text_upload_is_wired_without_writing_real_kb(monkeypatch):
    monkeypatch.setattr("app.service.upload", lambda path, filename=None: {"source": filename, "duplicate": False})
    response = client.post("/knowledge/upload", files={"file": ("safe.txt", "虚构测试内容".encode("utf-8"))})
    assert response.status_code == 200
    assert response.json()["source"] == "safe.txt"


def test_search_endpoint_is_wired(monkeypatch):
    monkeypatch.setattr("app.service.retrieve", lambda *args: [{"source": "demo.md"}])
    response = client.post("/rag/search", json={"query": "RAG", "top_k": 2})
    assert response.status_code == 200
    assert response.json()["results"][0]["source"] == "demo.md"
