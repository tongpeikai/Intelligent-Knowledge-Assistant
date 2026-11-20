# Usage

```powershell
$env:LLM_MODE='mock'
python main.py "RAG 是什么？"
python -m app.gradio_app
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000
python -m pytest -q
python -m scripts.evaluate_rag --output docs/RAG_EVALUATION_REPORT.md
```

真实 API 仅在用户主动设置 `LLM_MODE=api` 后启用。内置知识库只索引 3 个白名单示例文档；Web/API 上传保存到 Git 忽略的 `data/uploads/`。上传前请确认文件不含隐私或密钥，单文件默认上限 10 MB。

如需保护本地 API，在 `.env` 设置 `IKA_API_TOKEN`，请求携带 `Authorization: Bearer <token>`。默认限流为每客户端每分钟 60 次，可通过环境变量调整。服务命令始终绑定 `127.0.0.1`，不要直接暴露公网。

Gradio 会把完成后的 Agent 回答分块渐进显示。它改善显示体验，但工具链完成前仍需等待，不应描述为模型原生首 Token 流式输出。
