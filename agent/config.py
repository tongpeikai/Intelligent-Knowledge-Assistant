# ============================================================
# agent/config.py —— 全局配置中心
# ------------------------------------------------------------
# 所有路径、常量、System Prompt 都从这里取。
# 其他模块禁止再用 Path(__file__).parent 自己算路径。
# ============================================================

import os
from pathlib import Path
from dotenv import load_dotenv
# ---------- 路径 ----------
# __file__ = <project>/agent/config.py
# .resolve().parent       -> <project>/agent
# .resolve().parent.parent-> <project>
BASE_DIR = Path(__file__).resolve().parent.parent

# 加载 .env（在任何 os.environ 读取之前）
load_dotenv(BASE_DIR / ".env")

DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"
DB_PATH = BASE_DIR / "cities.db"
SESSIONS_DB_PATH = BASE_DIR / "sessions.db"
LOG_DIR = BASE_DIR / "logs"
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))

# ---------- 模型路径 ----------
# 嵌入模型路径：优先使用环境变量，否则使用相对路径
# 可通过环境变量 EMBEDDING_MODEL_PATH 覆盖
_configured_model_path = os.environ.get("EMBEDDING_MODEL_PATH")
_local_model_path = BASE_DIR / "models" / "bge-small-zh-v1.5"
_workspace_model_path = BASE_DIR.parent / "models" / "bge-small-zh-v1.5"
# A release clone does not carry model weights. On this workstation, reuse the
# sibling development workspace model without requiring a temporary env var.
EMBEDDING_MODEL_PATH = str(
    Path(_configured_model_path).expanduser()
    if _configured_model_path
    else (_local_model_path if _local_model_path.exists() else _workspace_model_path)
)

# ---------- LLM ----------
LLM_MODE = os.environ.get("LLM_MODE", "mock").strip().lower()
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")
LLM_TIMEOUT_SECONDS = float(os.environ.get("LLM_TIMEOUT_SECONDS", "30"))
LLM_MAX_RETRIES = int(os.environ.get("LLM_MAX_RETRIES", "2"))
SYSTEM_PROMPT = """你是一个严谨的助手。
调用工具失败时，根据错误信息决定是否重试或告知用户。
最终回答必须基于工具返回的真实数据。
不要替工具判断城市是否有效，把判断交给工具执行结果。
如果工具返回的数据明显不合理（例如火星天气、不存在的城市、与常识严重冲突），不要在回答中呈现该数据的具体数值，直接说明查询失败或数据不可靠，并建议用户换一个查询。
当用户询问技术概念、编程知识、项目文档相关内容时，必须先调用 search_docs 检索，基于检索结果回答。只有检索不到时才用通用知识补充，并明确标注"以下内容来自通用知识，非项目文档"。
当用户提问的问题具有时效性时，即使历史对话中包含了相同或相似的答案，你必须重新调用工具获取最新数据，严禁直接复述历史消息。

"""

# ---------- Agent 循环控制 ----------
MAX_STEPS = 10                   # 单次任务最大循环步数
MAX_REPEAT = 3                   # 同一工具+参数允许重复次数（P0 会用）

# ---------- 输入/输出约束 ----------
MAX_TOOL_RESULT_CHARS =  4000  # 工具返回内容最大字符数
MAX_QUESTION_CHARS = 2000        # 用户问题最大字符数
AGENT_TIMEOUT_SECONDS = 60       # 单次任务总耗时上限


# ---------- 记忆压缩 ----------
COMPRESS_THRESHOLD = 16      # 非 system 消息数超过此值触发压缩
COMPRESS_KEEP_RECENT = 8     # 压缩时至少保留最近 N 条消息不动
MAX_SUMMARY_CHARS = 500      # 摘要最大字符数（软上限）

# ---------- 高级 RAG ----------
ENABLE_QUERY_REWRITE = True   # 检索前用 LLM 改写 query
ENABLE_BILINGUAL_QUERY_EXPANSION = (
    os.environ.get("ENABLE_BILINGUAL_QUERY_EXPANSION", "true").strip().lower()
    in {"1", "true", "yes", "on"}
)  # 离线英文术语扩展，不调用 LLM
