import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _seed_one_respondent(workdir: Path) -> None:
    """Insert a synthetic prior respondent so the results page has a
    comparison trace. Runs in a subprocess so the SQLite file lands in the
    server's working directory."""
    script = (
        "import sys; sys.path.insert(0, sys.argv[1])\n"
        "import db, scds\n"
        "db.save_submission([\n"
        "    {'Process': 4, 'Compliance': 2, 'Autonomy': 1, 'Trust': 3}\n"
        "] * scds.NUM_QUESTIONS)\n"
    )
    subprocess.run(
        [sys.executable, "-c", script, str(REPO_ROOT)],
        cwd=workdir,
        check=True,
    )


@pytest.fixture(scope="session")
def app_url(tmp_path_factory):
    workdir = tmp_path_factory.mktemp("app")
    _seed_one_respondent(workdir)
    port = _free_port()
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "shiny",
            "run",
            "--port",
            str(port),
            str(REPO_ROOT / "app.py"),
        ],
        cwd=workdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
    )
    url = f"http://127.0.0.1:{port}"
    try:
        deadline = time.time() + 30
        while True:
            try:
                urllib.request.urlopen(url, timeout=1)
                break
            except Exception:
                if proc.poll() is not None or time.time() > deadline:
                    output = proc.stdout.read().decode(errors="replace")
                    raise RuntimeError(f"shiny server failed to start:\n{output}")
                time.sleep(0.3)
        yield url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
