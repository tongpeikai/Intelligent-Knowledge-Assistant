"""Evaluate document-level retrieval on a small, manually labeled fixture set."""

import argparse
import json
from pathlib import Path

from agent.config import BASE_DIR
from agent.rag import search_documents


DEFAULT_CASES = BASE_DIR / "tests" / "data" / "rag_eval_cases.json"


def evaluate(
    cases: list[dict],
    top_k: int = 3,
    max_distance: float = 2.0,
    expand_bilingual: bool = True,
) -> dict:
    rows = []
    recall_values, precision_values, rr_values = [], [], []
    no_answer_total = no_answer_rejected = 0
    for case in cases:
        hits = search_documents(
            case["query"], top_k=top_k, max_distance=max_distance,
            expand_bilingual=expand_bilingual,
        )
        relevant = set(case["relevant_sources"])
        hit_sources = [hit["source"] for hit in hits]
        if relevant:
            relevant_hits = sum(source in relevant for source in hit_sources)
            recalled = len(relevant.intersection(hit_sources)) / len(relevant)
            precision = relevant_hits / top_k
            first_rank = next((i for i, source in enumerate(hit_sources, 1) if source in relevant), None)
            rr = 1 / first_rank if first_rank else 0.0
            recall_values.append(recalled)
            precision_values.append(precision)
            rr_values.append(rr)
        else:
            recalled = precision = rr = None
            no_answer_total += 1
            filtered = search_documents(
                case["query"], top_k=top_k, max_distance=0.5,
                expand_bilingual=expand_bilingual,
            )
            no_answer_rejected += int(not filtered)
        rows.append({**case, "hits": hits, "recall": recalled, "precision": precision, "rr": rr})
    return {
        "top_k": top_k,
        "expand_bilingual": expand_bilingual,
        "labeled_answerable_cases": len(recall_values),
        "recall_at_k": sum(recall_values) / len(recall_values),
        "precision_at_k": sum(precision_values) / len(precision_values),
        "mrr": sum(rr_values) / len(rr_values),
        "no_answer_rejection": no_answer_rejected / no_answer_total if no_answer_total else None,
        "rows": rows,
    }


def _metrics_lines(label: str, result: dict) -> list[str]:
    return [
        f"### {label}",
        "",
        f"- Recall@{result['top_k']}: {result['recall_at_k']:.3f}",
        f"- Precision@{result['top_k']}: {result['precision_at_k']:.3f}",
        f"- MRR: {result['mrr']:.3f}",
        f"- No-answer rejection at distance <= 0.5: {result['no_answer_rejection']:.3f}",
        "",
    ]


def markdown(baseline: dict, result: dict) -> str:
    lines = [
        "# RAG Evaluation Report",
        "",
        "本报告使用项目内 8 条人工标注文档级测试问题。标注只表示预期来源文件，不是片段级完整相关性判断；结果仅代表当前小型测试集，不代表真实业务效果。无答案问题不参与 Recall/Precision/MRR，而单独统计阈值拒答率。",
        "",
        "## Before and after",
        "",
    ]
    lines += _metrics_lines("Baseline: vector retrieval only", baseline)
    lines += _metrics_lines("Optimized: deterministic bilingual term expansion", result)
    lines += [
        "优化只对命中的英文领域术语附加中文同义词，不调用 LLM、不下载翻译模型、不修改已有向量。基线和优化结果来自同一索引与同一标注集。",
        "",
        "Precision 分母固定为 K；同一相关文档的多个相关片段均按相关命中计算。Recall 按预期来源文档是否至少出现一次计算。",
        "",
        "## Per-case results",
        "",
        "| ID | Category | Expected | Retrieved (source: distance) | R@K | P@K | RR |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for row in result["rows"]:
        hits = "; ".join(f"{h['source']}:{h['distance']:.3f}" for h in row["hits"]) or "none"
        metrics = ["—" if row[key] is None else f"{row[key]:.3f}" for key in ("recall", "precision", "rr")]
        lines.append(
            f"| {row['id']} | {row['category']} | {', '.join(row['relevant_sources']) or 'no answer'} | {hits} | {metrics[0]} | {metrics[1]} | {metrics[2]} |"
        )
    lines += [
        "",
        "## Failure analysis",
        "",
        "- 跨文档问题要求两个来源均进入 Top-K，容易被较长的 `rag_basics.md` 多片段挤占；这是向量检索缺少来源去重/多样化的典型限制。",
        "- 英文语义问题在基线中受中文主体语料影响；轻量双语术语扩展改善该样例，但词表覆盖有限，不是通用机器翻译。",
        "- 无答案判断依赖距离阈值；单个合成问题不足以估计真实拒答率，需要业务问题与人工标注扩充后再下结论。",
        "- 指标是文档级弱标注；未对每个片段逐一判断相关性，因此不得解释为严格片段级检索精度。",
        "",
        "## Reproduce",
        "",
        "```powershell",
        "python -m scripts.evaluate_rag --output docs/RAG_EVALUATION_REPORT.md",
        "```",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--output", type=Path, default=BASE_DIR / "docs" / "RAG_EVALUATION_REPORT.md")
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    baseline = evaluate(cases, top_k=args.top_k, expand_bilingual=False)
    result = evaluate(cases, top_k=args.top_k, expand_bilingual=True)
    args.output.write_text(markdown(baseline, result), encoding="utf-8")
    summary = {
        "baseline": {k: v for k, v in baseline.items() if k != "rows"},
        "optimized": {k: v for k, v in result.items() if k != "rows"},
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
