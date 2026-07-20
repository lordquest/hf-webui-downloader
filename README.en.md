# HF WebUI Downloader

A cross-platform, graphical (WebUI) downloader for Hugging Face. Paste a repo page
URL or `owner/repo`, and it automatically lists the downloadable files (selectable);
click to download file-by-file with live progress, cancel, and retry.

## Features
- Parse `https://huggingface.co/<owner>/<repo>/tree/<revision>` or a bare `owner/repo`
- List repo files (name + size), selectable for download
- Configurable default download directory (empty = the tool's own directory), persisted
- Repo-isolated layout: files are stored under `<default dir>/<owner>-<repo>/`
- File-by-file download with a live progress bar + status (pending / downloading / done / exists / failed / cancelled)
- Per-file **Cancel** / **Retry**
- **Incremental append**: submit more files mid-download, merged into the same task
- **Resume**: a local file that already exists and is complete is skipped (status `exists`)
- **Mirror** support (set `HF_ENDPOINT`, e.g. `https://hf-mirror.com`)
- Under the hood: `huggingface_hub`'s native streaming chunked download + ETag/hash integrity verification

## Run
```bash
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:8000 in your browser
```

Or with uvicorn:
```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```

## Structure
- `app.py` —— FastAPI backend (parse / list / settings / download / SSE progress / cancel / retry)
- `hf_ops.py` —— core: `parse_repo_input` / `list_files` / `build_target_dir` / `DownloadTask`
- `config.py` —— persists default download dir and mirror endpoint (`config.json`)
- `static/index.html` —— pure static frontend (zero frontend framework)
- `requirements.txt`

## API
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/parse` | Parse repo input → repo_id/revision/subpath |
| POST | `/api/files` | List repo files |
| GET/POST | `/api/settings` | Read/write default download dir / mirror endpoint |
| POST | `/api/download` | Start or append a download (pass a `{path,size}` list) |
| GET | `/api/progress?task_id=` | SSE real-time progress stream |
| POST | `/api/cancel` | Cancel a single file |
| POST | `/api/retry` | Retry a single file |

## Author
- **lordquest**
- Email: lordquest@163.com
