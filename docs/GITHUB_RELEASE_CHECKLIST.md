# GitHub Release Checklist

## 可以上传

`agent/`、`app/`、`scripts/`、`tests/`、公开 `docs/`、`main.py`、`logging_config.py`、`requirements.txt`、`README.md`、`LICENSE`、`.gitignore`、`.env.example`。

`docs/assets/` 只能放经过人工隐私复核的演示截图；当前说明文件可上传，截图需用户最终检查后再添加。

## 必须忽略

`.env`/`.env.*`（保留 `.env.example`）、`models/`、`chroma_db/`、`logs/`、`*.db`/`*.sqlite*`、缓存、IDE 配置、`data/uploads/`、`local_only/`。本地学习笔记和完整内部验收报告只放 `local_only/`。

## 发布前命令

```powershell
git status --short
git diff --cached --name-status
git ls-files
git check-ignore .env models chroma_db sessions.db logs .idea .vscode local_only data/uploads
git grep -n -I -E "(sk-[A-Za-z0-9_-]{8,}|api.?key.*=|access.?token.*=|bearer [A-Za-z0-9._-]{12,}|password.*=|BEGIN .*PRIVATE KEY|[A-Z]:\\\\Users\\\\)"
git ls-files | ForEach-Object { Get-Item $_ } | Where-Object Length -gt 50MB
python -m pytest -q
```

同时检查未跟踪的公开候选文件，因为 `git grep` 只扫描已跟踪内容。确认无真实 Key、密码、私有地址、个人路径、用户资料、数据库、上传内容、模型权重、向量库、日志、缓存或大二进制。新电脑按 `INSTALLATION.md` 安装、复制环境模板、复用或单独获取 BGE，并仅在无索引时构建。保留 MIT License 和 Acaposa 原作者署名。
