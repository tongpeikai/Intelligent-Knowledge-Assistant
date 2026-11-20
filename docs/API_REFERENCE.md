# API Reference

启动后访问 `http://127.0.0.1:8000/docs` 查看交互文档。

- `GET /health`：状态和运行模式。
- `POST /chat`：问答及工具轨迹。
- `GET|POST /sessions`、`GET|DELETE /sessions/{id}`、`POST /sessions/{id}/clear`：会话管理。
- `POST /knowledge/upload`、`GET /knowledge/documents`：知识库管理。
- `POST /rag/search`：结构化检索。
- `GET /tools`：工具 Schema。

Pydantic 负责请求验证；不支持的上传类型返回 415；业务失败返回结构化 HTTP 错误。

## Security defaults

- 单文件默认最大 10 MB；验证安全文件名、扩展名、PDF 魔数和 UTF-8 文本内容。
- 上传保存到 Git 忽略的 `data/uploads/`。
- CORS 仅允许本机 Gradio 来源。
- 默认每客户端每分钟 60 次请求；超过返回 429。
- 设置 `IKA_API_TOKEN` 后，除健康检查和 API 文档外均要求 Bearer Token。
- 未处理异常只向客户端返回通用信息，详细堆栈仅写本地日志。

这些措施适合绑定 `127.0.0.1` 的单机演示。若要生产部署，需要 HTTPS、反向代理、持久化限流、密钥轮换和正式身份系统；本项目不会自动开放公网。
