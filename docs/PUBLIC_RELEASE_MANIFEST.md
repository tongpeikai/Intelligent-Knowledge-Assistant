# Public Release Manifest

## Repository tree

```text
Intelligent-Knowledge-Assistant/
├── agent/                 # Agent, tools, LLM, RAG and memory
├── app/                   # Shared service, FastAPI and Gradio
├── docs/                  # Public architecture, guides and evaluation
│   └── assets/            # Mock SVG placeholders or privacy-reviewed screenshots
├── scripts/               # Index and RAG evaluation commands
├── tests/                 # Unit, integration and security tests
│   └── data/              # Small public evaluation fixtures
├── .env.example           # Placeholder configuration
├── .gitignore
├── LICENSE                # Original MIT license / Acaposa attribution
├── README.md
├── eval_report.md
├── logging_config.py
├── main.py
└── requirements.txt
```

## Include in the public repository

- All source and test files under `agent/`, `app/`, `scripts/` and `tests/`.
- Public guides, Mermaid diagrams, weak-label RAG evaluation and Mock/fictional demo assets under `docs/`.
- Root entry points, dependency list, environment template, ignore rules, README and original license.

## Never include

- `.env` or any real API key/token/password.
- `models/`, `chroma_db/`, SQLite databases, `logs/`, caches or IDE state.
- `data/uploads/`, user documents or generated runtime content.
- `local_only/`, learning notes, debugging details or internal acceptance reports.
- Screenshots containing usernames, absolute paths, private session identifiers, browser profiles or unrelated applications; replace SVG placeholders only after privacy review.

## Current Git state

The local repository is intentionally uncommitted. The user must review `git status`, run the release checklist, select public files with `git add`, inspect the staged diff and only then create the first commit. No remote push is part of this project preparation.
