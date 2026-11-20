# RAG Evaluation Report

本报告使用项目内 8 条人工标注文档级测试问题。标注只表示预期来源文件，不是片段级完整相关性判断；结果仅代表当前小型测试集，不代表真实业务效果。无答案问题不参与 Recall/Precision/MRR，而单独统计阈值拒答率。

## Before and after

### Baseline: vector retrieval only

- Recall@3: 0.857
- Precision@3: 0.857
- MRR: 0.857
- No-answer rejection at distance <= 0.5: 1.000

### Optimized: deterministic bilingual term expansion

- Recall@3: 1.000
- Precision@3: 1.000
- MRR: 1.000
- No-answer rejection at distance <= 0.5: 1.000

优化只对命中的英文领域术语附加中文同义词，不调用 LLM、不下载翻译模型、不修改已有向量。基线和优化结果来自同一索引与同一标注集。

Precision 分母固定为 K；同一相关文档的多个相关片段均按相关命中计算。Recall 按预期来源文档是否至少出现一次计算。

## Per-case results

| ID | Category | Expected | Retrieved (source: distance) | R@K | P@K | RR |
|---|---|---|---|---:|---:|---:|
| zh_exact_fc | 中文/精确关键词 | function_calling.md | function_calling.md:0.215; function_calling.md:0.230; function_calling.md:0.257 | 1.000 | 1.000 | 1.000 |
| zh_semantic_chunk | 中文/语义问题 | rag_basics.md | rag_basics.md:0.323; rag_basics.md:0.344; rag_basics.md:0.366 | 1.000 | 1.000 | 1.000 |
| zh_incremental | 中文/语义问题 | rag_basics.md | rag_basics.md:0.351; rag_basics.md:0.354; rag_basics.md:0.365 | 1.000 | 1.000 | 1.000 |
| en_rag | 英文/语义问题 | rag_basics.md | rag_basics.md:0.356; rag_basics.md:0.362; rag_basics.md:0.376 | 1.000 | 1.000 | 1.000 |
| en_chroma | 英文/精确关键词 | chromadb_guide.md | chromadb_guide.md:0.281; chromadb_guide.md:0.294; chromadb_guide.md:0.322 | 1.000 | 1.000 | 1.000 |
| cross_rag_chroma | 跨文档 | rag_basics.md, chromadb_guide.md | chromadb_guide.md:0.310; rag_basics.md:0.323; rag_basics.md:0.326 | 1.000 | 1.000 | 1.000 |
| zh_distance | 中文/精确概念 | rag_basics.md | rag_basics.md:0.266; rag_basics.md:0.302; rag_basics.md:0.306 | 1.000 | 1.000 | 1.000 |
| no_answer | 知识库无答案 | no answer | rag_basics.md:0.659; rag_basics.md:0.674; rag_basics.md:0.683 | — | — | — |

## Failure analysis

- 跨文档问题要求两个来源均进入 Top-K，容易被较长的 `rag_basics.md` 多片段挤占；这是向量检索缺少来源去重/多样化的典型限制。
- 英文语义问题在基线中受中文主体语料影响；轻量双语术语扩展改善该样例，但词表覆盖有限，不是通用机器翻译。
- 无答案判断依赖距离阈值；单个合成问题不足以估计真实拒答率，需要业务问题与人工标注扩充后再下结论。
- 指标是文档级弱标注；未对每个片段逐一判断相关性，因此不得解释为严格片段级检索精度。

## Reproduce

```powershell
python -m scripts.evaluate_rag --output docs/RAG_EVALUATION_REPORT.md
```
