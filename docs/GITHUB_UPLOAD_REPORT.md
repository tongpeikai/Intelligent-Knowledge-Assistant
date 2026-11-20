# GitHub Upload Report

审核日期：2026-11-20。本文是基于当前工作区实际文件的发布前审计；不会执行 `git add`、commit 或 push。

## Executive result

- Git 暂存区：空。
- Git 已跟踪文件：0；Git 历史：无 commit。
- 审计开始时公开候选文件：63 个。此前记录的 59 个候选不包含本次新增的 4 个 SVG 占位图；因此本报告按实际文件清单记录为 63 个。报告写入后，公开候选自然增加为 64 个。
- `pytest -q`：57 passed，0 failed，0 skipped。
- ChromaDB：72 条，未修改。
- 公开候选超过 5 MB：0 个。
- 公开凭据扫描：无真实 Key/Token/密码命中。
- 真实 API 调用：0 次。
- 新增下载和依赖安装：0。

## Privacy audit

### Secret handling

- `.env` 仅检查存在性和 Git 忽略状态，未读取、打印、复制或外传内容。
- `.env` 被忽略；`.env.example` 未被忽略并只含虚构占位符。
- 扫描 README、源码、测试、公开文档、未跟踪候选和 Git 历史；Git 历史为空，没有需要轮换或清理的提交。
- 扫描命中的 `DEEPSEEK_API_KEY` 仅是变量名/占位符或代码读取环境变量，不是真实凭据。
- 截图占位图不含 API Key 管理页面、密钥复制记录、日志、账号、个人路径或运行数据；正式截图必须继续使用 Mock 和虚构数据。

### Required local-only paths

`.env`、`models/`、`chroma_db/`、`cities.db`、`sessions.db`、其他 SQLite 文件、`logs/`、`data/uploads/`、`local_only/`、`__pycache__/`、`.pytest_cache/`、`.idea/` 和 `.vscode/` 均通过 `git check-ignore`。它们不能进入公开提交。

## File-by-file public candidate review

风险含义：`无` 表示公开内容不含本地数据；`模板` 表示仅有虚构配置占位符；`需人工复核` 仅适用于未来替换的截图，不适用于当前 SVG 占位图。

| Path | Bytes | Upload reason | Privacy risk |
|---|---:|---|---|
| `.env.example` | 1089 | Public configuration template | 模板；无真实值 |
| `.gitignore` | 460 | Defines release boundary | 无 |
| `LICENSE` | 1064 | Original MIT terms and attribution | 无；保留 Acaposa |
| `README.md` | 8634 | Public setup, features and demo entry | 无；不得填写真实 Key |
| `agent/__init__.py` | 218 | Python package marker | 无 |
| `agent/config.py` | 3601 | Paths, runtime settings and limits | 仅读取环境变量名；无密钥值 |
| `agent/llm_client.py` | 3273 | Mock/API client implementation | 读取本地环境变量；无密钥值 |
| `agent/loop.py` | 8555 | Agent orchestration | 无 |
| `agent/memory.py` | 6201 | Session context and summaries | 无 |
| `agent/models.py` | 695 | Result/trace data models | 无 |
| `agent/rag.py` | 14807 | Parsing, indexing and retrieval | 无；不含向量数据 |
| `agent/session_store.py` | 3481 | SQLite persistence adapter | 仅代码；数据库被忽略 |
| `agent/tools.py` | 9052 | Tool schemas and registry | 无；天气工具不含账号 |
| `app/__init__.py` | 29 | Python package marker | 无 |
| `app/api.py` | 5847 | FastAPI boundary and upload security | 仅环境变量名；无 token |
| `app/gradio_app.py` | 3279 | Local Gradio UI | 无；仅本地回环地址 |
| `app/service.py` | 1752 | Shared application service | 无 |
| `docs/AGENT_GUIDE.md` | 500 | Public Agent explanation | 无 |
| `docs/API_REFERENCE.md` | 1192 | Public API reference | 无 |
| `docs/ARCHITECTURE.md` | 6021 | Public architecture and flow diagrams | 无 |
| `docs/CAREER_PROJECT_DESCRIPTION.md` | 3148 | Resume-ready project description | 无；测试指标有局限说明 |
| `docs/DEMO_GUIDE.md` | 2179 | Public demo and screenshot rules | 无；要求 Mock/虚构数据 |
| `docs/FINAL_RELEASE_REPORT.md` | 2361 | Sanitized release status | 无内部凭据或绝对路径 |
| `docs/GITHUB_RELEASE_CHECKLIST.md` | 1474 | Release verification commands | 无 |
| `docs/GRADIO_GUIDE.md` | 665 | Gradio startup guide | 无 |
| `docs/INSTALLATION.md` | 1132 | New-machine installation | 无个人环境值 |
| `docs/INTERVIEW_GUIDE.md` | 4440 | Interview preparation | 无 |
| `docs/LLM_API_GUIDE.md` | 485 | Mock/API behavior | 无真实 Key |
| `docs/MEMORY_GUIDE.md` | 499 | SQLite memory guide | 无数据库内容 |
| `docs/PROJECT_SHOWCASE.md` | 4272 | Technology map and engineering highlights | 无 |
| `docs/PUBLIC_RELEASE_MANIFEST.md` | 1886 | Public/local file policy | 无 |
| `docs/RAG_EVALUATION_REPORT.md` | 3075 | Reproducible retrieval evidence | 无本地数据；弱标注局限已说明 |
| `docs/RAG_GUIDE.md` | 1313 | RAG operation guide | 无 |
| `docs/USAGE.md` | 934 | Public usage commands | 无 |
| `docs/assets/README.md` | 377 | Screenshot asset policy | 无 |
| `docs/assets/agent-tool-trace.svg` | 937 | Mock tool-flow placeholder | 纯占位图；无隐私 |
| `docs/assets/gradio-chat.svg` | 832 | Mock Gradio placeholder | 纯占位图；无隐私 |
| `docs/assets/memory-session.svg` | 919 | Fictional memory placeholder | 纯占位图；无真实 Session ID |
| `docs/assets/rag-sources.svg` | 782 | Mock source-result placeholder | 纯占位图；无隐私 |
| `docs/chromadb_guide.md` | 1912 | Allowlisted public knowledge source | 无 |
| `docs/function_calling.md` | 778 | Allowlisted public knowledge source | 无 |
| `docs/rag_basics.md` | 9022 | Allowlisted public knowledge source | 无 |
| `eval_report.md` | 340 | Public pointer to RAG evaluation | 无 |
| `logging_config.py` | 1211 | Logging setup | 无；不写 Key |
| `main.py` | 2199 | CLI entry point | 无 |
| `requirements.txt` | 223 | Reproducible dependency ranges | 无 |
| `scripts/__init__.py` | 0 | Python package marker | 无 |
| `scripts/eval.py` | 13473 | Existing evaluation script | 仅代码；无运行数据 |
| `scripts/evaluate_rag.py` | 6028 | Reproducible RAG metrics | 无；读取公开 fixture |
| `scripts/rebuild_index.py` | 967 | Index construction entry point | 无；不包含 Chroma data |
| `tests/__init__.py` | 20 | Test package marker | 无 |
| `tests/conftest.py` | 1208 | Test fixtures | 使用临时/虚构数据 |
| `tests/data/rag_eval_cases.json` | 1315 | Public weak-label fixture | 虚构技术问题；无个人数据 |
| `tests/test_agent_deep.py` | 3953 | Agent edge-case tests | 虚构参数 |
| `tests/test_api.py` | 3372 | API and upload security tests | 虚构 token/test data |
| `tests/test_gradio.py` | 620 | Gradio construction/stream tests | 虚构数据 |
| `tests/test_llm_mock.py` | 894 | Mock LLM tests | 不调用真实 API |
| `tests/test_loop.py` | 3829 | Agent loop tests | Mock responses only |
| `tests/test_memory.py` | 4141 | Memory/session tests | 临时虚构数据 |
| `tests/test_rag.py` | 1755 | RAG helper tests | 无个人数据 |
| `tests/test_rag_evaluation.py` | 793 | Metric calculation test | 虚构 fixture |
| `tests/test_rag_management.py` | 3226 | Incremental RAG tests | 临时文件；无真实上传 |
| `tests/test_tools.py` | 1462 | Tool validation tests | 虚构城市/用户 fixture |

## Local-only inventory

These paths must remain local and are not part of the public candidate list:

- `.env`
- `models/`
- `chroma_db/`
- `cities.db`, `sessions.db` and other SQLite files
- `logs/`
- `data/uploads/`
- `local_only/` including `README_LOCAL.md` and internal acceptance reports
- `__pycache__/`, `.pytest_cache/`, `.idea/`, `.vscode/`

## Manual actions still required

1. Review the 63-file snapshot above and decide whether to include `docs/GITHUB_UPLOAD_REPORT.md` itself; it is safe and sanitized but is added after the 63-file snapshot.
2. Keep the staging area empty until review is complete.
3. If replacing SVG placeholders with screenshots, capture in Mock mode using fictional data and repeat the privacy scan.
4. Run `git add` only after manual review; inspect `git diff --cached`; do not stage any local-only path.
5. Create a commit and push only through a separate, explicit user action.

## Final judgement

The public candidate set is suitable for GitHub review. The application and tests are ready for local demonstration; real DeepSeek API behavior remains intentionally unverified. No secret was read, printed, copied, transmitted or committed during this audit.
