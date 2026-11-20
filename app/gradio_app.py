"""Gradio UI backed by the shared application service."""

import gradio as gr

from agent.llm_client import get_mode
from app import service


def _new_session():
    sid = service.new_session_id()
    return sid, [], f"已新建会话 `{sid}`"


def _load_session(session_id: str):
    messages = service.history(session_id)
    chat = [{"role": m["role"], "content": m.get("content") or ""} for m in messages]
    return chat, f"已加载 {len(chat)} 条消息"


def _clear(session_id: str):
    service.clear_session(session_id)
    return [], "会话已清空"


def _chat_stream(message: str, history: list, session_id: str):
    """渐进渲染回答；后端 Agent 完成后按小块推送，无新增依赖。"""
    if not message.strip():
        yield history, "请输入问题", ""
        return
    result = service.chat(message, session_id)
    updated = list(history or [])
    updated.append({"role": "user", "content": message})
    answer = result["answer"] if result["success"] else f"错误：{result['aborted_reason']}"
    trace = "\n".join(
        f"- {item['name']} ({item['duration_ms']} ms): {item.get('error') or '成功'}"
        for item in result["trace"]
    ) or "本轮未调用工具"
    updated.append({"role": "assistant", "content": ""})
    for end in range(1, len(answer) + 1, 8):
        streamed = [*updated[:-1], {"role": "assistant", "content": answer[:end + 7]}]
        yield streamed, trace, ""
    if not answer:
        yield updated, trace, ""


def _upload(file_path: str | None):
    if not file_path:
        return "请选择文件"
    result = service.upload(file_path)
    return f"已索引 {result['source']}；重复={result['duplicate']}；集合总数={result['collection_count']}"


def build_demo() -> gr.Blocks:
    mode = get_mode().upper()
    with gr.Blocks(title="Intelligent Knowledge Assistant") as demo:
        gr.Markdown(f"# Intelligent Knowledge Assistant\n\n**当前模式：{mode}**（Mock 不会发起付费 API 请求）")
        session_id = gr.Textbox(value=service.new_session_id(), label="会话 ID")
        status = gr.Markdown("就绪")
        with gr.Row():
            new_btn = gr.Button("新建会话")
            load_btn = gr.Button("加载会话")
            clear_btn = gr.Button("清空会话")
        chatbot = gr.Chatbot(label="对话")
        message = gr.Textbox(label="消息", placeholder="请输入问题并回车")
        trace = gr.Markdown("本轮未调用工具")
        with gr.Row():
            upload = gr.File(label="导入 PDF / TXT / Markdown", type="filepath", file_types=[".pdf", ".txt", ".md", ".markdown"])
            upload_btn = gr.Button("构建知识库")
        upload_status = gr.Markdown()

        message.submit(_chat_stream, [message, chatbot, session_id], [chatbot, trace, message])
        new_btn.click(_new_session, outputs=[session_id, chatbot, status])
        load_btn.click(_load_session, inputs=session_id, outputs=[chatbot, status])
        clear_btn.click(_clear, inputs=session_id, outputs=[chatbot, status])
        upload_btn.click(_upload, inputs=upload, outputs=upload_status)
    return demo


demo = build_demo()


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, show_error=True)
