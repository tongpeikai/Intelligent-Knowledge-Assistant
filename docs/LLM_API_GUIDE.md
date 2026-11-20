# LLM API Guide

默认配置是 `LLM_MODE=mock`，不读取 Key、不联网、不产生费用，输出明确带 `[Mock 模式]`。

真实模式需用户主动设置 `LLM_MODE=api`，并在本地 `.env` 配置 `DEEPSEEK_API_KEY`。可配置 `LLM_BASE_URL`、`LLM_MODEL`、`LLM_TIMEOUT_SECONDS` 和 `LLM_MAX_RETRIES`。缺 Key 会明确失败；SDK 负责兼容 OpenAI 接口、超时、有限重试和流式响应。余额错误不会无限重试。本次验收未调用真实 API。
