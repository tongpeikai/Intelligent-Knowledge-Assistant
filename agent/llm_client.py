"""DeepSeek/OpenAI-compatible client with an offline-first Mock mode."""

import json
import os
from types import SimpleNamespace
from typing import Iterable

from openai import OpenAI

from agent.config import LLM_BASE_URL, LLM_MAX_RETRIES, LLM_MODE, LLM_MODEL, LLM_TIMEOUT_SECONDS

_client = None


class MockCompletions:
    """Deterministic local model used for development; never performs network I/O."""

    @staticmethod
    def _response(content=None, tool_calls=None):
        message = SimpleNamespace(content=content, tool_calls=tool_calls or [])
        return SimpleNamespace(
            choices=[SimpleNamespace(message=message)],
            usage=SimpleNamespace(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            model="mock-local",
        )

    def create(self, *, messages, tools=None, stream=False, **kwargs):
        last = messages[-1] if messages else {"role": "user", "content": ""}
        if last.get("role") == "tool":
            content = f"[Mock 模式] 根据工具返回结果：\n{last.get('content', '')}"
            return self._stream(content) if stream else self._response(content)
        text = str(last.get("content") or "")
        lowered = text.lower()
        if tools and any(k in lowered for k in ("rag", "文档", "知识库", "function calling", "chromadb")):
            call = SimpleNamespace(
                id="mock-search-1",
                function=SimpleNamespace(
                    name="search_docs",
                    arguments=json.dumps({"query": text}, ensure_ascii=False),
                ),
            )
            return self._response(None, [call])
        content = f"[Mock 模式] 已收到：{text}"
        return self._stream(content) if stream else self._response(content)

    @staticmethod
    def _stream(content: str) -> Iterable:
        for piece in content:
            yield SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=piece))])


class MockLLMClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=MockCompletions())
        self.is_mock = True


def get_mode() -> str:
    mode = os.environ.get("LLM_MODE", LLM_MODE).strip().lower()
    if mode not in {"mock", "api"}:
        raise RuntimeError("LLM_MODE 必须是 mock 或 api")
    return mode


def get_client():
    """Get a cached client. Mock is the safe default and does not read the API key."""
    global _client
    mode = get_mode()
    if _client is not None and bool(getattr(_client, "is_mock", False)) == (mode == "mock"):
        return _client
    if mode == "mock":
        _client = MockLLMClient()
        return _client
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key or api_key.startswith("sk-your-"):
        raise RuntimeError("API 模式缺少有效的 DEEPSEEK_API_KEY，请检查 .env。")
    _client = OpenAI(
        api_key=api_key,
        base_url=os.environ.get("LLM_BASE_URL", LLM_BASE_URL),
        timeout=LLM_TIMEOUT_SECONDS,
        max_retries=LLM_MAX_RETRIES,
    )
    _client.is_mock = False
    return _client


def model_name() -> str:
    return "mock-local" if get_mode() == "mock" else os.environ.get("LLM_MODEL", LLM_MODEL)


def reset_client() -> None:
    global _client
    _client = None
