"""FastAPI backend for the Hugging Face WebUI downloader.

Endpoints:
  GET  /                       -> serve frontend
  POST /api/parse              -> parse repo URL/id -> {repo_id, repo_type, revision, subpath}
  POST /api/files              -> list files in a repo
  GET  /api/settings           -> current settings
  POST /api/settings           -> save settings (download_dir, endpoint)
  POST /api/download           -> start/append download (returns task_id)
  GET  /api/progress?task_id=  -> SSE stream of per-file progress
  POST /api/cancel             -> cancel one file
  POST /api/retry              -> retry one file
"""
import asyncio
import json
import queue
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

import config as cfg

# huggingface_hub is the core download dependency; if it (or its deps) is missing,
# the app must still start so the WebUI can show an install hint rather than crash.
try:
    import hf_ops  # noqa: F401
    HF_OPS_OK = True
except Exception as _imp_err:  # pragma: no cover - depends on environment
    hf_ops = None
    HF_OPS_OK = False
    _HF_OPS_ERR = str(_imp_err)

app = FastAPI(title="HF WebUI Downloader")
BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"

# Critical third-party dependencies required for downloading.
_REQUIRED_DEPS = ["fastapi", "uvicorn", "huggingface_hub", "tqdm"]


def check_deps() -> dict:
    """Return which required deps are importable; never raises."""
    missing = []
    for name in _REQUIRED_DEPS:
        try:
            __import__(name)
        except Exception:
            missing.append(name)
    if not HF_OPS_OK and hf_ops is None:
        # hf_ops failed to import -> almost certainly huggingface_hub missing
        if "huggingface_hub" not in missing:
            missing.append("huggingface_hub")
    return {
        "missing": missing,
        "install_cmd": "pip install -r requirements.txt",
        "ok": len(missing) == 0,
    }


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/health")
async def health():
    return JSONResponse(check_deps())


def _require_hf_ops():
    """Return an error JSONResponse if hf_ops is unavailable, else None."""
    if hf_ops is None:
        return JSONResponse(
            {"error": "缺少核心依赖 huggingface_hub,无法下载。请运行: pip install -r requirements.txt 后重启。"},
            status_code=503,
        )
    return None


@app.post("/api/parse")
async def parse(req: Request):
    guard = _require_hf_ops()
    if guard is not None:
        return guard
    body = await req.json()
    text = body.get("input", "")
    try:
        return JSONResponse(hf_ops.parse_repo_input(text))
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.post("/api/files")
async def files(req: Request):
    guard = _require_hf_ops()
    if guard is not None:
        return guard
    body = await req.json()
    repo_id = body.get("repo_id", "")
    revision = body.get("revision", "main")
    subpath = body.get("subpath", "")
    repo_type = body.get("repo_type", "model")
    settings = cfg.load_config()
    endpoint = settings.get("endpoint", "")
    try:
        listing = hf_ops.list_files(repo_id, revision, subpath, repo_type, endpoint)
        return JSONResponse({"files": listing})
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": f"列举失败: {e}"}, status_code=400)


@app.get("/api/target_dir")
async def target_dir(repo_id: str = ""):
    guard = _require_hf_ops()
    if guard is not None:
        return guard
    if not repo_id:
        return JSONResponse({"error": "缺少 repo_id"}, status_code=400)
    settings = cfg.load_config()
    base_dir = settings.get("download_dir") or str(BASE)
    return JSONResponse({"repo_id": repo_id, "target_dir": hf_ops.target_dir_for(repo_id, base_dir)})


@app.get("/api/settings")
async def get_settings():
    return JSONResponse(cfg.load_config())


@app.post("/api/settings")
async def post_settings(req: Request):
    body = await req.json()
    dd = body.get("download_dir")
    ep = body.get("endpoint")
    lang = body.get("language")
    saved = cfg.save_settings(download_dir=dd, endpoint=ep, language=lang)
    return JSONResponse(saved)


@app.get("/api/token")
async def token_status():
    guard = _require_hf_ops()
    if guard is not None:
        return guard
    status = hf_ops.check_hf_token()
    # persist only the boolean detection result, never the token itself
    cfg.save_settings(hf_logged_in=(status["status"] == "logged_in"))
    return JSONResponse(status)


@app.post("/api/token/login")
async def token_login(req: Request):
    guard = _require_hf_ops()
    if guard is not None:
        return guard
    body = await req.json()
    token = body.get("token", "")
    result = hf_ops.login_hf_token(token)
    if result.get("status") == "logged_in":
        cfg.save_settings(hf_logged_in=True)
    else:
        cfg.save_settings(hf_logged_in=False)
    return JSONResponse(result)


@app.post("/api/download")
async def download(req: Request):
    guard = _require_hf_ops()
    if guard is not None:
        return guard
    body = await req.json()
    repo_id = body.get("repo_id", "")
    revision = body.get("revision", "main")
    repo_type = body.get("repo_type", "model")
    files = body.get("files", [])
    # accept either [{path,size}] or plain [path,...]
    norm = []
    for f in files:
        if isinstance(f, dict):
            norm.append((f.get("path"), int(f.get("size", 0) or 0)))
        else:
            norm.append((f, 0))
    task_id = body.get("task_id") or uuid.uuid4().hex[:12]

    settings = cfg.load_config()
    base_dir = settings.get("download_dir") or str(BASE)
    endpoint = settings.get("endpoint", "")
    target_dir = str(hf_ops.build_target_dir(repo_id, base_dir))

    task = hf_ops.get_or_create_task(
        task_id, repo_id, repo_type, revision, target_dir, endpoint)
    task.add_files(norm)
    return JSONResponse({
        "task_id": task_id,
        "target_dir": target_dir,
        "files": task.snapshot(),
    })


@app.post("/api/cancel")
async def cancel(req: Request):
    guard = _require_hf_ops()
    if guard is not None:
        return guard
    body = await req.json()
    task_id = body.get("task_id", "")
    path = body.get("path", "")
    task = hf_ops.TASKS.get(task_id)
    if not task:
        return JSONResponse({"error": "任务不存在"}, status_code=404)
    task.cancel_file(path)
    return JSONResponse({"ok": True})


@app.post("/api/retry")
async def retry(req: Request):
    guard = _require_hf_ops()
    if guard is not None:
        return guard
    body = await req.json()
    task_id = body.get("task_id", "")
    path = body.get("path", "")
    task = hf_ops.TASKS.get(task_id)
    if not task:
        return JSONResponse({"error": "任务不存在"}, status_code=404)
    task.retry_file(path)
    return JSONResponse({"ok": True})


@app.get("/api/progress")
async def progress(task_id: str, request: Request):
    task = hf_ops.TASKS.get(task_id)
    if not task:
        return JSONResponse({"error": "任务不存在"}, status_code=404)

    q: "queue.Queue" = queue.Queue()

    def on_update(path, state):
        # Called from worker threads; queue.Queue is thread-safe.
        try:
            q.put_nowait({"type": "update", "file": state})
        except Exception:
            pass

    task.subscribe(on_update)

    async def event_stream():
        # initial snapshot
        yield "data: " + json.dumps({"type": "snapshot",
                                      "files": task.snapshot()}) + "\n\n"
        try:
            while True:
                if await request.is_disconnected():
                    break
                if task.is_done() and q.empty():
                    break
                try:
                    item = await asyncio.wait_for(
                        asyncio.to_thread(q.get, True, 1.0), timeout=1.0)
                    yield "data: " + json.dumps(item) + "\n\n"
                except (asyncio.TimeoutError, queue.Empty):
                    yield ": ping\n\n"
        finally:
            yield "data: " + json.dumps({"type": "done",
                                          "files": task.snapshot()}) + "\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
