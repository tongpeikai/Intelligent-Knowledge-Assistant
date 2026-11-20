# Gradio Guide

```powershell
$env:LLM_MODE='mock'
D:\Anaconda\envs\ai_assistant\python.exe -m app.gradio_app
```

打开 `http://127.0.0.1:7860`。界面支持多轮聊天、新建/加载/清空会话、PDF/TXT/Markdown 上传、知识库增量构建和工具轨迹展示。上传会进入真实 RAG 流程并保存在 Git 忽略目录；Mock 标识始终可见。

回答会按小块渐进渲染，使用现有 Gradio 能力且无需新增依赖。当前 Agent 必须先完成工具闭环，因此这不是模型原生首 Token 流式传输；若未来需要降低首字延迟，应为 Agent 循环增加异步事件流，而不是在 UI 中伪称原生流式。
