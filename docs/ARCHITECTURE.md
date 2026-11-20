# Architecture

```mermaid
flowchart LR
  CLI[CLI] --> S[Application Service]
  UI[Gradio] --> S
  API[FastAPI] --> S
  S --> A[Agent Loop]
  A <--> L[Mock / DeepSeek Client]
  A --> T[Tool Registry]
  T --> R[RAG: BGE + ChromaDB]
  A --> M[Memory: SQLite]
  R --> D[3 built-in docs]
  R --> U[Ignored data/uploads]
```

入口不包含核心业务；`app.service` 统一编排。Agent 只依赖客户端、工具与会话接口。RAG 使用本地 BGE 生成 512 维向量，并通过 Chroma 持久化。公开 `docs/` 中只有 3 个显式白名单文件进入知识库，工程文档不会被误索引；用户上传进入 Git 忽略的 `data/uploads/`。

FastAPI 边界包含大小/内容/文件名验证、本地 CORS、可选 Bearer Token、内存限流和异常脱敏。认证与限流面向单机演示；多进程生产部署应改用反向代理或共享限流存储。所有路径由 `agent.config` 基于项目根目录计算，兼容 Windows。

## Module responsibilities

| Module | Responsibility |
|---|---|
| `agent/config.py` | Relative paths, environment variables and runtime limits |
| `agent/llm_client.py` | Offline Mock and OpenAI-compatible DeepSeek client |
| `agent/loop.py` | Multi-step Agent orchestration and tool result feedback |
| `agent/tools.py` | Tool schemas, validation, registry, timeout and retry |
| `agent/rag.py` | Parsing, chunking, embedding, indexing and retrieval |
| `agent/memory.py` / `session_store.py` | In-memory context, summaries and SQLite persistence |
| `app/service.py` | UI/API-independent use cases |
| `app/api.py` | Validated and hardened HTTP boundary |
| `app/gradio_app.py` | Local interactive demonstration UI |

## Core request flow

```mermaid
sequenceDiagram
  actor User
  participant Entry as CLI / Gradio / FastAPI
  participant Service
  participant Agent
  participant LLM as Mock / DeepSeek
  participant Tool
  participant Memory as SQLite Memory
  User->>Entry: question + session_id
  Entry->>Service: chat()
  Service->>Memory: restore session
  Service->>Agent: run_agent()
  Agent->>LLM: messages + tool schemas
  alt tool call returned
    LLM-->>Agent: name + JSON arguments
    Agent->>Tool: validate and execute
    Tool-->>Agent: result / controlled error
    Agent->>LLM: role=tool result
  end
  LLM-->>Agent: final answer
  Agent->>Memory: persist messages
  Agent-->>Entry: answer + trace
  Entry-->>User: response
```

## LLM API request and response

```mermaid
sequenceDiagram
  participant Agent
  participant Client as llm_client.py
  participant Mock as MockCompletions
  participant API as DeepSeek OpenAI-compatible API
  Agent->>Client: get_client().chat.completions.create()
  alt LLM_MODE=mock (default)
    Client->>Mock: messages + tools + tool_choice=auto
    Mock-->>Client: local response / structured tool_calls
  else LLM_MODE=api (explicit)
    Client->>API: model + messages + tools + timeout
    API-->>Client: assistant message, tool_calls and usage
  end
  Client-->>Agent: choices[0].message
  Agent->>Agent: persist assistant message
```

The request includes the system prompt, current session messages, registered tool schemas and automatic tool choice. A normal response has `message.content` and no tool calls. A tool response has `message.tool_calls[]`, where each item contains a call ID, function name and JSON arguments. API errors are caught by the Agent boundary; Mock mode never makes a network request and API mode is never enabled implicitly.

## RAG result into Agent context

```mermaid
sequenceDiagram
  participant LLM
  participant Agent
  participant Search as search_docs
  participant RAG as Chroma + BGE
  LLM-->>Agent: tool_call(search_docs, {query})
  Agent->>Search: validate query and execute
  Search->>RAG: embed query + query top_k
  RAG-->>Search: documents, metadata, distances
  Search-->>Agent: formatted source/chunk/page/distance text
  Agent->>Agent: append role=tool with matching tool_call_id
  Agent->>LLM: original context + tool result
  LLM-->>Agent: grounded final answer or next tool_call
```

The tool result is bounded by `MAX_TOOL_RESULT_CHARS`; source, chunk/page and distance remain visible to the model and the UI trace. If no result passes the distance threshold, the explicit “没有找到足够相关的文档内容” result is returned, allowing the model to state the limitation rather than inventing a citation.

## Failure and exception path

```mermaid
flowchart TD
  A[LLM or tool step] --> B{Failure type}
  B -->|invalid JSON| C[Record json_decode error]
  B -->|invalid/extra argument| D[Record schema error]
  B -->|unknown/dangerous tool| E[Reject before execution]
  B -->|timeout/exception| F[Retry bounded, then return controlled error]
  B -->|same signature repeated| G[Inject corrective feedback]
  C --> H[Append role=tool feedback]
  D --> H
  E --> H
  F --> H
  G --> H
  H --> I{steps and total time remain?}
  I -->|yes| A
  I -->|no| J[AgentResult success=false and reason]
```

FastAPI converts failed service results to safe HTTP responses; unhandled exceptions are logged locally and redacted to clients. The UI displays a user-readable error and keeps the session trace. No failure branch prints API keys or local absolute paths.

## RAG flow

```mermaid
flowchart LR
  F[PDF / TXT / Markdown] --> V[Type and content validation]
  V --> P[Parse text and PDF pages]
  P --> C[Paragraph/sentence chunking]
  C --> E[BGE-small-zh-v1.5 embedding]
  E --> DB[(ChromaDB cosine index)]
  Q[Question] --> X[Optional bilingual term expansion]
  X --> QE[Query embedding]
  QE --> DB
  DB --> K[Top-K + distance threshold]
  K --> S[Content + source + chunk/page + distance]
```

## Data boundaries

- Public sample corpus: three explicitly allowlisted Markdown files.
- Local uploads: `data/uploads/`, ignored by Git.
- Runtime state: `chroma_db/`, SQLite databases and `logs/`, ignored by Git.
- Private notes/reports: `local_only/`, ignored by Git.
- Secrets: `.env`, ignored by Git; `.env.example` contains placeholders only.
