# RAG Guide

支持 `.pdf`、`.txt`、`.md`、`.markdown`。`agent.rag.sync_index()` 对文档计算 MD5，未变化文件跳过；变化文件先按 `source` 替换旧向量；磁盘删除会在同步时清理索引。元数据包括文件名、片段号、文件类型、文件哈希和 PDF 页码。

```powershell
D:\Anaconda\envs\ai_assistant\python.exe -m scripts.rebuild_index
```

日常应使用增量同步，`force_rebuild=True` 会重建集合，只有明确备份和授权时才使用。公开 `docs/` 中只有 `chromadb_guide.md`、`function_calling.md`、`rag_basics.md` 会被索引，工程文档不会混入知识库；用户上传保存在 Git 忽略的 `data/uploads/`。

检索可调用 `search_documents(query, top_k, max_distance)` 获取结构化来源，或 `search_docs()` 获取适合交给 LLM 的文本。文本型 PDF 可直接解析；扫描 PDF 不含可提取文本时需另配 OCR。固定弱标注评估可运行 `python -m scripts.evaluate_rag`，指标定义和局限见 `RAG_EVALUATION_REPORT.md`。

英文技术查询默认使用小型确定性术语表追加中文同义词，可通过 `ENABLE_BILINGUAL_QUERY_EXPANSION=false` 关闭。它不联网、不调用 LLM，也不是通用翻译器；评估报告同时运行关闭和开启两种模式，避免隐藏基线。
