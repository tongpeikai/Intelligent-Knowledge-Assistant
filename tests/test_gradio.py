def test_gradio_builds(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "mock")
    from app.gradio_app import build_demo
    demo = build_demo()
    assert demo is not None


def test_chat_progressively_streams(monkeypatch):
    from app import gradio_app
    monkeypatch.setattr(gradio_app.service, "chat", lambda *args: {
        "answer": "这是一个足够长的流式回答", "success": True, "trace": [], "aborted_reason": None
    })
    updates = list(gradio_app._chat_stream("问题", [], "sid"))
    assert len(updates) >= 2
    assert updates[-1][0][-1]["content"] == "这是一个足够长的流式回答"
