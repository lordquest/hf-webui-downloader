"""Core Hugging Face operations: parse repo input, list files, build isolated
target dir, and download files one-by-one with progress / cancel / retry / append / resume.

All downloads use huggingface_hub.hf_hub_download with local_dir +
local_dir_use_symlinks=False. huggingface_hub performs chunked streaming
downloads with ETag/size integrity checks and auto-retries on failure.
"""
from __future__ import annotations

import os
import re
import threading
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlparse

from huggingface_hub import HfApi, hf_hub_download, login, get_token
from huggingface_hub.utils import GatedRepoError, RepositoryNotFoundError
from tqdm.auto import tqdm as _BaseTqdm

# Statuses
STATUS_PENDING = "pending"
STATUS_DOWNLOADING = "downloading"
STATUS_DONE = "done"
STATUS_EXISTS = "exists"  # already present & complete -> skipped (resume)
STATUS_FAILED = "failed"
STATUS_CANCELLED = "cancelled"


class _ProgressTqdm(_BaseTqdm):
    """tqdm subclass that forwards progress to a callback `(current, total)`.

    huggingface_hub drives this during the real HTTP download, so reported
    progress matches the CLI tqdm exactly (it reads the actual byte stream,
    not a temp file we have to guess the location of)."""

    def __init__(self, *args, _on_progress=None, **kwargs):
        self._on_progress = _on_progress
        self._seen = 0
        # we drive our own web progress; suppress huggingface's CLI bar
        kwargs["disable"] = True
        super().__init__(*args, **kwargs)

    def update(self, n=1):
        super().update(n)
        if self._on_progress is not None:
            self._seen += n
            total = self.total or 0
            self._on_progress(self._seen, total)

    def reset(self, total=None):
        super().reset(total)
        self._seen = 0
        if self._on_progress is not None:
            self._on_progress(0, total or 0)


def parse_repo_input(text: str) -> dict:
    """Parse a HF web URL or bare `owner/repo` into repo_id / revision / subpath.

    Accepts:
      - https://huggingface.co/SC117/Agents-.../tree/main
      - https://huggingface.co/SC117/Agents-.../tree/main/some/subdir
      - https://huggingface.co/datasets/owner/repo/...
      - owner/repo
      - owner/repo@revision
      - owner/repo@revision/sub/path
    """
    text = (text or "").strip()
    repo_type = "model"
    revision = "main"
    subpath = ""

    if text.startswith("http://") or text.startswith("https://"):
        parsed = urlparse(text)
        parts = [p for p in parsed.path.split("/") if p]
        # possible leading "datasets" / "spaces"
        if parts and parts[0] in ("datasets", "spaces", "models"):
            repo_type = parts[0].rstrip("s")  # datasets->dataset, spaces->space, models->model
            parts = parts[1:]
        if len(parts) >= 2:
            owner, repo = parts[0], parts[1]
            rest = parts[2:]
            if rest and rest[0] == "tree":
                rest = rest[1:]
                if rest:
                    revision = rest[0]
                    subpath = "/".join(rest[1:])
            elif rest:
                # blob/resolve/resolve/main/... etc -> treat leading as revision? keep simple
                subpath = "/".join(rest)
            repo_id = f"{owner}/{repo}"
        else:
            raise ValueError("无法从 URL 解析出仓库标识")
    else:
        # bare owner/repo with optional @revision and /subpath
        m = re.match(r"^([^/@]+)/([^/@]+)(?:@([^/]+))?(?:/(.*))?$", text)
        if not m:
            raise ValueError("无法解析仓库标识,期望格式 owner/repo 或完整 HF 网址")
        owner, repo, rev, sub = m.group(1), m.group(2), m.group(3), m.group(4)
        repo_id = f"{owner}/{repo}"
        if rev:
            revision = rev
        if sub:
            subpath = sub

    return {
        "repo_id": repo_id,
        "repo_type": repo_type,
        "revision": revision,
        "subpath": subpath,
    }


def list_files(repo_id: str, revision: str = "main", subpath: str = "",
               repo_type: str = "model", endpoint: str = "") -> list:
    """List files under repo_id (+ subpath) with sizes (bytes)."""
    api = HfApi(endpoint=endpoint or None)
    results = []
    try:
        tree = api.list_repo_tree(
            repo_id, revision=revision, path_in_repo=subpath or None,
            repo_type=repo_type, recursive=True,
        )
    except RepositoryNotFoundError:
        raise ValueError(f"仓库不存在或无权访问: {repo_id}")
    except GatedRepoError:
        raise ValueError(f"该仓库为受限(gated)仓库,需先授权: {repo_id}")

    for node in tree:
        # Tree object: RepoFile has .size and .path ; RepoFolder has .path only
        if getattr(node, "tree_id", None) is None and hasattr(node, "size"):
            # RepoFile-like
            path = node.path
            if subpath and path == subpath:
                continue
            results.append({"path": path, "size": int(getattr(node, "size", 0) or 0)})
    return results


def target_dir_for(repo_id: str, base_dir: str) -> str:
    """Compute (without creating) the isolated target dir `<owner>-<repo>` under base_dir."""
    safe = repo_id.replace("/", "-")
    return str(Path(base_dir) / safe)


def build_target_dir(repo_id: str, base_dir: str) -> Path:
    """Build isolated dir `<owner>-<repo>` under base_dir (replace '/' with '-')."""
    target = Path(target_dir_for(repo_id, base_dir))
    target.mkdir(parents=True, exist_ok=True)
    return target


# ---------------------------------------------------------------------------
# Download task manager
# ---------------------------------------------------------------------------

class DownloadTask:
    """Manages a set of file downloads for one repo_id, with live progress."""

    def __init__(self, repo_id: str, repo_type: str, revision: str,
                 target_dir: str, endpoint: str, max_workers: int = 3):
        self.repo_id = repo_id
        self.repo_type = repo_type
        self.revision = revision
        self.target_dir = target_dir
        self.endpoint = endpoint
        self.max_workers = max_workers
        self.files: dict[str, dict] = {}      # path -> file state
        self._lock = threading.Lock()
        self._cancel = threading.Event()
        self._sem = threading.Semaphore(max_workers)
        self._threads: list[threading.Thread] = []
        self._subscribers: list[Callable] = []
        self.finished = False

    # -- progress subscription (for SSE) --
    def subscribe(self, cb: Callable[[str, dict], None]):
        with self._lock:
            self._subscribers.append(cb)

    def _emit(self, path: str):
        state = self.files[path]
        for cb in self._subscribers:
            try:
                cb(path, state)
            except Exception:
                pass

    def _set(self, path: str, **kw):
        with self._lock:
            self.files[path].update(kw)
        self._emit(path)

    # -- task control --
    def add_files(self, files):
        """Add files to the task, starting download threads for new ones.
        `files` is a list of (path, size) tuples. Supports incremental append."""
        new = []
        with self._lock:
            for item in files:
                if isinstance(item, tuple):
                    p, size = item
                else:
                    p, size = item, 0
                if p not in self.files:
                    self.files[p] = {
                        "path": p,
                        "status": STATUS_PENDING,
                        "downloaded": 0,
                        "total": size,
                        "speed": 0.0,
                    }
                    new.append(p)
                elif self.files[p]["status"] in (STATUS_FAILED, STATUS_CANCELLED):
                    self.files[p]["status"] = STATUS_PENDING
                    self.files[p]["downloaded"] = 0
                    if size:
                        self.files[p]["total"] = size
                    new.append(p)
        for p in new:
            t = threading.Thread(target=self._worker, args=(p,), daemon=True)
            self._threads.append(t)
            t.start()

    def _worker(self, path: str):
        self._sem.acquire()
        try:
            if self._cancel.is_set() or self.files[path]["status"] == STATUS_CANCELLED:
                return
            self._set(path, status=STATUS_DOWNLOADING)

            # resume check: local file already complete?
            local_path = os.path.join(self.target_dir, path)
            total = self.files[path].get("total") or 0
            if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                existing = os.path.getsize(local_path)
                if total and existing >= total:
                    self._set(path, status=STATUS_EXISTS, downloaded=existing, total=existing)
                    return

            import time
            last_t = time.time()
            last_b = 0

            def _on_progress(downloaded, tot):
                nonlocal last_t, last_b
                now = time.time()
                dt = now - last_t
                speed = (downloaded - last_b) / dt if dt > 0.3 else 0.0
                if dt > 0.3:
                    last_t, last_b = now, downloaded
                self._set(path, downloaded=downloaded,
                          total=tot or total, speed=speed * 1_000_000 if speed else 0.0)

            tqdm_cls = lambda *a, **k: _ProgressTqdm(*a, **k, _on_progress=_on_progress)
            try:
                hf_hub_download(
                    repo_id=self.repo_id,
                    filename=path,
                    repo_type=self.repo_type,
                    revision=self.revision,
                    local_dir=self.target_dir,
                    endpoint=self.endpoint or None,
                    tqdm_class=tqdm_cls,
                )
                size = os.path.getsize(local_path) if os.path.exists(local_path) else 0
                if self._cancel.is_set():
                    self._set(path, status=STATUS_CANCELLED)
                else:
                    self._set(path, status=STATUS_DONE, downloaded=size, total=size or total)
            except Exception as e:
                if self._cancel.is_set():
                    self._set(path, status=STATUS_CANCELLED)
                else:
                    self._set(path, status=STATUS_FAILED, error=str(e)[:300])
        finally:
            self._sem.release()
            self._check_finished()

    def _check_finished(self):
        with self._lock:
            active = [f for f in self.files.values()
                      if f["status"] in (STATUS_PENDING, STATUS_DOWNLOADING)]
            if not active and not self.finished:
                # only mark finished if no pending threads; cheap check
                alive = [t for t in self._threads if t.is_alive()]
                if not alive:
                    self.finished = True

    def cancel_file(self, path: str):
        with self._lock:
            if path in self.files and self.files[path]["status"] in (
                STATUS_PENDING, STATUS_DOWNLOADING):
                self.files[path]["status"] = STATUS_CANCELLED
        self._emit(path)

    def retry_file(self, path: str):
        with self._lock:
            if path in self.files and self.files[path]["status"] in (
                STATUS_FAILED, STATUS_CANCELLED):
                self.files[path]["status"] = STATUS_PENDING
                self.files[path]["downloaded"] = 0
        t = threading.Thread(target=self._worker, args=(path,), daemon=True)
        self._threads.append(t)
        t.start()

    def is_done(self) -> bool:
        with self._lock:
            return all(f["status"] not in (STATUS_PENDING, STATUS_DOWNLOADING)
                       for f in self.files.values())

    def snapshot(self) -> list:
        with self._lock:
            return [dict(f) for f in self.files.values()]


# Global registry of tasks (by task_id)
TASKS: dict[str, DownloadTask] = {}
_TASK_LOCK = threading.Lock()


def get_or_create_task(task_id: str, repo_id: str, repo_type: str,
                       revision: str, target_dir: str, endpoint: str) -> DownloadTask:
    with _TASK_LOCK:
        if task_id not in TASKS:
            TASKS[task_id] = DownloadTask(
                repo_id, repo_type, revision, target_dir, endpoint)
        return TASKS[task_id]


# ---------------------------------------------------------------------------
# Hugging Face token detection & login
# ---------------------------------------------------------------------------

def check_hf_token() -> dict:
    """Detect local HF token status.

    Returns one of:
      {"status": "logged_in"}  -> token present and whoami succeeds
      {"status": "invalid"}    -> token present but whoami fails (revoked/expired)
      {"status": "missing"}    -> no token at all
    Token itself is never returned.
    """
    token = None
    try:
        token = get_token()
    except Exception:
        token = None
    if not token:
        return {"status": "missing"}
    try:
        HfApi().whoami(token=token)
        return {"status": "logged_in"}
    except Exception:
        return {"status": "invalid"}


def login_hf_token(token: str) -> dict:
    """Login (non-interactively, equivalent to `huggingface-cli login`) by
    persisting the token to the local default location. Does NOT write to
    config.json. Returns the re-checked status afterwards."""
    token = (token or "").strip()
    if not token:
        return {"status": "missing", "error": "token 为空"}
    try:
        login(token=token)  # persists to ~/.cache/huggingface/token
    except Exception as e:
        return {"status": "invalid", "error": str(e)[:300]}
    return check_hf_token()
