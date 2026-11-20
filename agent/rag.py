# ============================================================
# agent/rag.py —— RAG 检索模块（增量更新版）
# ------------------------------------------------------------
# 原 rag_store.py 迁移而来。路径统一从 agent.config 取。
# ============================================================

import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import hashlib
import json
import logging
import shutil
from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from agent.config import CHROMA_DIR, DOCS_DIR, EMBEDDING_MODEL_PATH, UPLOAD_DIR


logger = logging.getLogger("rag")

BILINGUAL_TERMS = {
    "retrieval augmented generation": "检索增强生成 RAG",
    "retrieval-augmented generation": "检索增强生成 RAG",
    "hallucination": "幻觉",
    "hallucinations": "幻觉",
    "vector database": "向量数据库",
    "embedding": "嵌入模型 向量",
    "embeddings": "嵌入模型 向量",
    "chunking": "文本切分 分片",
    "similarity": "相似度",
    "cosine": "余弦",
    "persistent client": "持久化客户端 PersistentClient",
    "metadata": "元数据 来源",
    "function calling": "函数调用 工具调用",
    "tool calls": "工具调用 tool_calls",
    "json schema": "参数模式 JSON Schema",
    "incremental index": "增量索引",
    "reduce": "减少",
}

# 模块级缓存
_client = None
_collection = None
_file_hashes: dict[str, str] = {}
# 中文嵌入模型（惰性加载，首次调用时下载/加载）
_embedding_fn = None

# 文件哈希持久化路径（放在 chroma 目录下，便于统一清理）
HASH_FILE = CHROMA_DIR / "file_hashes.json"
SUPPORTED_SUFFIXES = {".md", ".markdown", ".txt", ".pdf"}
BUILTIN_KNOWLEDGE_FILES = {"chromadb_guide.md", "function_calling.md", "rag_basics.md"}


def _load_hashes() -> None:
    """从磁盘加载文件哈希映射，使增量索引跨进程生效。"""
    global _file_hashes
    if HASH_FILE.exists():
        try:
            _file_hashes = json.loads(HASH_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"[RAG] 读取哈希文件失败：{e}，回退为空映射")
            _file_hashes = {}
    else:
        _file_hashes = {}


def _save_hashes() -> None:
    """把当前文件哈希映射写回磁盘。"""
    try:
        HASH_FILE.parent.mkdir(exist_ok=True)
        HASH_FILE.write_text(
            json.dumps(_file_hashes, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        logger.warning(f"[RAG] 写入哈希文件失败：{e}")


def get_embedding_fn():
    global _embedding_fn
    if _embedding_fn is None:
        _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_PATH
        )
        logger.info(f"[RAG] 嵌入模型已加载: {EMBEDDING_MODEL_PATH}")
    return _embedding_fn


def chunk_text(text: str, max_len: int = 300) -> list[str]:
    """按段落切分长文本，段落超长则按句子切分；单句超长则硬切。"""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    for p in paragraphs:
        if len(p) <= max_len:
            chunks.append(p)
            continue

        # 按标点插入换行，再按行拼接
        for sep in ["。", "；", "，", "\n"]:
            p = p.replace(sep, sep + "\n")
        sentences = p.split("\n")

        buf = ""
        for s in sentences:
            if len(buf) + len(s) <= max_len:
                buf += s
                continue

            if buf:
                chunks.append(buf)
                buf = ""

            # 单句本身就超长：硬切
            while len(s) > max_len:
                chunks.append(s[:max_len])
                s = s[max_len:]

            buf = s

        if buf:
            chunks.append(buf)
    return chunks


def file_hash(fp: Path) -> str:
    return hashlib.md5(fp.read_bytes()).hexdigest()


def parse_document(fp: Path) -> list[dict[str, Any]]:
    """解析支持的文档，返回带页码的文本单元。"""
    suffix = fp.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(f"不支持的文件类型：{suffix or '无扩展名'}")
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(fp))
        pages = []
        for page_no, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                pages.append({"text": text, "page": page_no})
        return pages
    text = fp.read_text(encoding="utf-8-sig")
    return [{"text": text, "page": None}]


def _document_files(directory: Path) -> dict[str, Path]:
    if not directory.exists():
        return {}
    return {
        fp.name: fp for fp in directory.iterdir()
        if fp.is_file() and fp.suffix.lower() in SUPPORTED_SUFFIXES
    }


def get_collection():
    """获取或创建 ChromaDB 文档集合（带缓存）。"""
    global _client, _collection

    if _collection is not None:
        return _collection

    CHROMA_DIR.mkdir(exist_ok=True)
    _client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    try:
        _collection = _client.get_collection(
            "docs",
            embedding_function=get_embedding_fn()
        )
        logger.info("[RAG] 使用已有集合")
    except Exception:
        _collection = _client.create_collection(
            "docs",
            embedding_function=get_embedding_fn(),
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("[RAG] 创建新集合（cosine 空间）")

    return _collection


def sync_index(force_rebuild: bool = False):
    """增量同步文档索引到 ChromaDB。"""
    global _collection, _file_hashes

    collection = get_collection()

    if force_rebuild:
        try:
            _client.delete_collection("docs")
        except Exception:
            pass
        _collection = _client.create_collection(
            "docs",
            embedding_function=get_embedding_fn(),
            metadata={"hnsw:space": "cosine"}
        )
        collection = _collection
        _file_hashes = {}
        _save_hashes()
        logger.info("[RAG] 强制全量重建")
    else:
        # 从磁盘恢复上次的哈希映射，避免每次新进程都全量重嵌入
        _load_hashes()

    if not DOCS_DIR.exists():
        logger.warning(f"[RAG] 文档目录不存在: {DOCS_DIR}")
        return collection

    # docs/ also contains public engineering documentation; only the explicit
    # built-in knowledge corpus is indexed. User uploads live in ignored storage.
    current_files = {
        name: fp for name, fp in _document_files(DOCS_DIR).items()
        if name in BUILTIN_KNOWLEDGE_FILES
    }
    for name, fp in _document_files(UPLOAD_DIR).items():
        if name in current_files:
            logger.warning("[RAG] 上传文件与公开文档同名，跳过：%s", name)
            continue
        current_files[name] = fp
    current_hashes = {name: file_hash(fp) for name, fp in current_files.items()}

    # 删除已移除的文件
    for old_name in list(_file_hashes.keys()):
        if old_name not in current_files:
            collection.delete(where={"source": old_name})
            logger.info(f"[RAG] 删除已移除文档: {old_name}")
            del _file_hashes[old_name]

    # 处理新增或修改的文件
    for name, fp in current_files.items():
        new_hash = current_hashes[name]
        if _file_hashes.get(name) == new_hash:
            continue

        collection.delete(where={"source": name})

        docs, ids, metadatas = [], [], []
        chunk_no = 0
        for unit in parse_document(fp):
            for chunk in chunk_text(unit["text"]):
                docs.append(chunk)
                ids.append(hashlib.sha256(f"{name}:{chunk_no}".encode()).hexdigest())
                metadata = {
                    "source": name,
                    "chunk": chunk_no,
                    "file_hash": new_hash,
                    "file_type": fp.suffix.lower(),
                }
                if unit["page"] is not None:
                    metadata["page"] = unit["page"]
                metadatas.append(metadata)
                chunk_no += 1

        if docs:
            collection.add(documents=docs, ids=ids, metadatas=metadatas)
            logger.info(f"[RAG] 更新文档: {name}，{len(docs)} 个片段")

        _file_hashes[name] = new_hash

    _save_hashes()
    return collection


def rewrite_query(query: str) -> str:
    """用 LLM 把用户问题改写成更适合向量检索的形式。"""
    from agent.config import ENABLE_QUERY_REWRITE
    if not ENABLE_QUERY_REWRITE:
        return query
    from agent.llm_client import get_client, get_mode, model_name
    if get_mode() == "mock":
        return query
    prompt = (
        "把下面的用户问题改写成一句简洁的中文检索查询。"
        "要求：保留关键实体和意图，去掉口语化词（如'帮我'、'请问'、'你知道'）。"
        "只输出改写后的查询本身，不要解释、不要引号。\n\n"
        f"原问题：{query}"
    )
    try:
        resp = get_client().chat.completions.create(
            model=model_name(), messages=[{"role": "user", "content": prompt}], temperature=0,
        )
        rewritten = (resp.choices[0].message.content or "").strip()
        if rewritten and rewritten != query:
            logger.info("[QueryRewrite] '%s' → '%s'", query, rewritten)
        return rewritten or query
    except Exception as exc:
        logger.warning("[QueryRewrite] 失败：%s，回退原 query", exc)
        return query


def expand_bilingual_query(query: str) -> str:
    """为命中的英文领域术语追加中文同义词，不联网、不调用模型。"""
    lowered = query.lower()
    additions = []
    for term, translation in BILINGUAL_TERMS.items():
        if term in lowered and translation not in additions:
            additions.append(translation)
    return f"{query} {' '.join(additions)}" if additions else query


def search_docs(query: str, top_k: int = 3, max_distance: float = 0.5) -> str:
    """
    检索本地知识库，返回相关文档片段。

    参数：
        query: 用户查询文本
        top_k: 返回的最相关片段数量
        max_distance: 最大距离阈值，超过则过滤
    """
    hits = search_documents(query, top_k=top_k, max_distance=max_distance)
    if not hits:
        return "没有找到足够相关的文档内容"
    parts = []
    for hit in hits:
        page = f" 第{hit['page']}页" if hit.get("page") else ""
        parts.append(
            f"[来源: {hit['source']}{page} 第{hit['chunk']}段 | 距离:{hit['distance']:.2f}]\n"
            f"{hit['content']}"
        )
    return "\n\n---\n\n".join(parts)


def search_documents(
    query: str,
    top_k: int = 3,
    max_distance: float = 0.5,
    expand_bilingual: bool | None = None,
) -> list[dict]:
    """结构化检索，供 API、Gradio 和来源展示复用。"""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query 不能为空")
    if top_k < 1 or top_k > 50:
        raise ValueError("top_k 必须在 1 到 50 之间")
    query = rewrite_query(query.strip())
    if expand_bilingual is None:
        from agent.config import ENABLE_BILINGUAL_QUERY_EXPANSION
        expand_bilingual = ENABLE_BILINGUAL_QUERY_EXPANSION
    if expand_bilingual:
        query = expand_bilingual_query(query)
    collection = sync_index()

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    logger.info(f"[检索] query='{query}' 距离: {[round(d, 2) for d in dists]}")

    hits = []
    for d, m, dist in zip(docs, metas, dists):
        if dist > max_distance:
            continue
        hits.append({
            "content": d,
            "source": m.get("source", "unknown"),
            "chunk": m.get("chunk", 0),
            "page": m.get("page"),
            "distance": float(dist),
        })
    return hits


def index_document(source: str | Path, destination_dir: Path | None = None) -> dict:
    """安全复制上传文档并增量索引；同名同内容不会重复写入。"""
    src = Path(source).resolve()
    if not src.is_file():
        raise FileNotFoundError(f"文件不存在：{src.name}")
    if src.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError("仅支持 PDF、TXT、Markdown 文件")
    target_dir = (destination_dir or UPLOAD_DIR).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / src.name
    _load_hashes()
    duplicate = (
        (_file_hashes.get(target.name) == file_hash(src))
        if src == target
        else (target.exists() and file_hash(target) == file_hash(src))
    )
    if not duplicate and src != target:
        shutil.copy2(src, target)
    before = get_collection().count()
    sync_index()
    return {
        "source": target.name,
        "duplicate": duplicate,
        "collection_count": get_collection().count(),
        "count_change": get_collection().count() - before,
    }


def delete_document(source_name: str, remove_file: bool = False) -> int:
    """从索引删除指定来源；默认保留磁盘原文件。"""
    if Path(source_name).name != source_name:
        raise ValueError("source_name 只能是文件名")
    collection = get_collection()
    before = collection.count()
    collection.delete(where={"source": source_name})
    _load_hashes()
    _file_hashes.pop(source_name, None)
    _save_hashes()
    if remove_file:
        target = DOCS_DIR / source_name
        if target.exists():
            target.unlink()
    return before - collection.count()


def list_documents() -> list[dict]:
    """列出知识库文件及其索引状态。"""
    _load_hashes()
    files = {
        name: fp for name, fp in _document_files(DOCS_DIR).items()
        if name in BUILTIN_KNOWLEDGE_FILES
    }
    files.update({k: v for k, v in _document_files(UPLOAD_DIR).items() if k not in files})
    return [
        {"source": name, "size": fp.stat().st_size, "indexed": name in _file_hashes}
        for name, fp in sorted(files.items())
    ]


def rebuild_all():
    """强制全量重建文档索引。"""
    sync_index(force_rebuild=True)
    logger.info("[RAG] 全量重建完成")
