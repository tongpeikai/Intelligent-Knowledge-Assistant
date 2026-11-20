# Final Release Report

日期：2026-11-20。此公开报告仅记录可复现的发布状态；完整内部审计仍保存在被忽略的 `local_only/private_reports/FINAL_PROJECT_ACCEPTANCE_REPORT.md`。

## Release decision

**Ready for manual GitHub release review.** The application runs in Mock mode without paid API access, the public README is sufficient for a new developer to install and run the project, and the code/test/documentation boundary is explicit. No commit or remote push has been performed.

## Verified results

- `pytest -q`: 57 passed, 0 failed, 0 skipped.
- `compileall`: passed.
- BGE loaded from the local model directory.
- ChromaDB remained at 72 chunks from the three allowlisted sample documents.
- Mock Agent completed a RAG tool-call round trip and retained follow-up context.
- FastAPI `/health` and `/chat` returned HTTP 200 on `127.0.0.1`.
- Gradio returned HTTP 200 on `127.0.0.1`.
- Public credential/path scan: clean; no public file over 5 MB.

## RAG evidence

The fixed 8-case document-level weak-label set records the original vector-only baseline (Recall@3/Precision@3/MRR: 0.857/0.857/0.857) and the deterministic bilingual-term result (1.000/1.000/1.000). The report documents the dataset, parameters, distances, reproduction command and limitations; these are not production accuracy claims.

## Upload categories

### Public

`agent/`, `app/`, `scripts/`, `tests/`, public `docs/`, `README.md`, `requirements.txt`, `LICENSE`, `.gitignore`, `.env.example`, `main.py`, `logging_config.py` and `eval_report.md`.

### Local only

`.env`, `models/`, `chroma_db/`, SQLite files, `logs/`, `data/uploads/`, `local_only/`, caches, IDE state and any unreviewed screenshots.

## Manual release steps

1. Run `docs/GITHUB_RELEASE_CHECKLIST.md` commands.
2. Review `git status --short` and select only public files with `git add`.
3. Inspect `git diff --cached`, including the README and screenshots.
4. Confirm secrets, databases, models, uploads, logs and `local_only` are absent.
5. Create a local commit only after review; push or publish manually later.

## Known limits

Real DeepSeek billing/API behavior, OCR, production identity, HTTPS, shared rate limiting and native first-token streaming remain intentionally unverified or deferred. No new dependency or model download was required for this release preparation.
