"""Regression tests for the Gradio visible ID/current-state synchronization."""

from unittest.mock import patch


def test_new_session_returns_one_id_for_display_and_backend_state():
    from app import gradio_app

    with patch.object(gradio_app.service, "new_session_id", return_value="A-2026"):
        assert gradio_app._new_session() == ("A-2026", [], "已新建会话 `A-2026`", "A-2026")


def test_load_session_returns_requested_id_as_current_state():
    from app import gradio_app

    with patch.object(
        gradio_app.service,
        "history",
        return_value=[{"role": "user", "content": "A-only"}],
    ) as history:
        chat, status, current_id = gradio_app._load_session(" A-2026 ")

    history.assert_called_once_with(" A-2026 ")
    assert chat == [{"role": "user", "content": "A-only"}]
    assert "1" in status
    assert current_id == "A-2026"


def test_chat_uses_backend_current_session_state_not_stale_visible_history(monkeypatch):
    from app import gradio_app

    calls = []
    monkeypatch.setattr(
        gradio_app.service,
        "chat",
        lambda message, session_id: calls.append((message, session_id)) or {
            "answer": "A answer", "success": True, "trace": [], "aborted_reason": None
        },
    )
    list(gradio_app._chat_stream("A question", [{"role": "user", "content": "B-only"}], "A-2026"))
    assert calls == [("A question", "A-2026")]
