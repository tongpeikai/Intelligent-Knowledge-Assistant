from agent.llm_client import MockLLMClient, get_client, reset_client
from agent.loop import run_agent


def test_mock_is_default(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "mock")
    reset_client()
    assert isinstance(get_client(), MockLLMClient)


def test_mock_direct_chat(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "mock")
    reset_client()
    result = run_agent("你好")
    assert result.success
    assert result.answer.startswith("[Mock 模式]")


def test_mock_tool_call_round_trip(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "mock")
    reset_client()
    monkeypatch.setattr("agent.loop.execute_tool_with_retry", lambda *_: "RAG 是检索增强生成")
    result = run_agent("RAG 文档是什么？")
    assert result.success
    assert result.steps == 2
    assert result.tool_calls[0].name == "search_docs"
    assert "工具返回结果" in result.answer
