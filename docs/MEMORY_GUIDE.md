# Memory Guide

`AgentSession` 保存 system/user/assistant/tool 角色消息。传入 `session_id` 后，消息和滚动摘要持久化到本地 `sessions.db`。`load_or_create()` 恢复历史；`list_sessions()` 列表；`clear_session()` 保留 ID 并清空；`delete_session()` 删除指定会话。

超过 `COMPRESS_THRESHOLD` 时仅压缩旧的完整对话链，保留最近消息。Mock 模式下摘要不会产生付费请求。SQLite 异常会记录警告并保证主流程可控返回。
