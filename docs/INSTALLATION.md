# Installation

推荐 Python 3.10。以下两种方式二选一；如果本机已有可用的 Python/Conda 环境，不要重装 PyTorch、CUDA 或已有模型。

## Existing Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

## New Conda environment

仅在新电脑没有合适环境时执行：

```powershell
conda create -n intelligent-knowledge-assistant python=3.10 -y
conda activate intelligent-knowledge-assistant
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

## Local embedding model

将 `BAAI/bge-small-zh-v1.5` 放到 `models/bge-small-zh-v1.5`，或用 `EMBEDDING_MODEL_PATH` 指向已有本地目录。不要在已有模型可用时重复下载。当前 Windows 工作区的发布目录会在自身模型目录不存在时回退查找同级开发目录的 `models/bge-small-zh-v1.5`；这只适用于本机开发验收，不会把模型复制到 GitHub。首次部署且不存在 Chroma 数据时，执行 `python -m scripts.rebuild_index`；已有正常索引时不要强制重建。

验证：

```powershell
$env:LLM_MODE='mock'
python -m pytest -q
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000
```

模型、数据库、上传文件和 `.env` 均不得上传 GitHub。
