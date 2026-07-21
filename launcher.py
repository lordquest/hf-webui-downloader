"""Entry point for the packaged single-file exe.

In source mode this is unused (run via ``uvicorn app:app``).
In PyInstaller onefile mode, ``launcher.py`` is the entry script:
  - opens the default browser after a short delay
  - starts uvicorn serving ``app.app`` on 127.0.0.1:8000
"""
import sys
import threading
import time
import webbrowser

import uvicorn

from app import app as fastapi_app  # noqa: E402


def _open_browser(port: int = 8000, delay: float = 1.2) -> None:
    time.sleep(delay)
    webbrowser.open(f"http://127.0.0.1:{port}")


def main() -> None:
    port = 8000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    # Open browser in a daemon thread so it doesn't block shutdown.
    t = threading.Thread(target=_open_browser, args=(port,), daemon=True)
    t.start()

    uvicorn.run(
        fastapi_app,
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )


if __name__ == "__main__":
    main()
