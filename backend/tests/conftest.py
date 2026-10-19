"""Keep SHUFFL tests bound to this repository's ``backend/app`` package.

The development machine also has another project exposing a top-level
``app`` package. Pytest's default path ordering could import that package
instead of SHUFFL's API, producing misleading collection failures.
"""

import os
import atexit
import json
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import socket
from pathlib import Path
import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_ROOT.parent
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))

# Tests must never mutate the developer's configured production/local MySQL.
TEST_DB_PATH = Path(tempfile.gettempdir()) / f"shuffl_test_{os.getpid()}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH.as_posix()}"
os.environ["APP_ENV"] = "test"
os.environ["ADMIN_API_TOKEN"] = ""
os.environ["ADMIN_ROLE_TOKENS"] = ""

# If a parent pytest/plugin imported another top-level app package first,
# remove it so the path above resolves SHUFFL's package deterministically.
loaded_app = sys.modules.get("app")
if loaded_app is not None:
    loaded_path = str(getattr(loaded_app, "__file__", ""))
    if str(BACKEND_ROOT / "app") not in loaded_path:
        for module_name in list(sys.modules):
            if module_name == "app" or module_name.startswith("app."):
                del sys.modules[module_name]


class _Response:
    def __init__(self, status_code: int, body: bytes):
        self.status_code = status_code
        self._body = body

    def json(self):
        return json.loads(self._body.decode("utf-8"))


class SyncASGITestClient:
    """Small HTTP facade backed by an isolated Uvicorn subprocess.

    The subprocess boundary matches deployment. Restricted runners can opt
    into the direct/unit test subset with ``SHUFFL_SKIP_SOCKET_TESTS=1``;
    normal local Windows runs keep the real HTTP boundary.
    """

    # This class is a test transport, not a pytest test class.
    __test__ = False
    _process = None
    _base_url = None
    _socket_unavailable = False

    def __init__(self, app=None, base_url: str = "http://testserver", **_: object):
        # Start lazily so importing a test module never blocks collection.
        pass

    @classmethod
    def _ensure_server(cls):
        if cls._socket_unavailable and os.getenv("SHUFFL_ALLOW_SOCKET_TESTS", "0").lower() not in {"1", "true", "yes"}:
            pytest.skip("Loopback ASGI test server is unavailable in this environment; set SHUFFL_ALLOW_SOCKET_TESTS=1 to run socket-bound API contract tests.")
        if cls._process is not None and cls._process.poll() is None:
            return
        env = os.environ.copy()
        # The API imports the sibling venue_pipeline_backend package. The
        # subprocess cwd is backend/, so explicitly preserve the repository
        # root on PYTHONPATH for the real HTTP test boundary.
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = os.pathsep.join(
            item for item in (str(PROJECT_ROOT), existing_pythonpath) if item
        )
        configured_port = os.environ.get("SHUFFL_TEST_PORT", "").strip()
        candidates: list[int] = []
        if configured_port:
            candidates.append(int(configured_port))
        # A fixed development port can be reserved by Windows or another
        # local process. Keep the explicit port as the first choice, then use
        # an ephemeral loopback port so the contract tests remain portable.
        allow_socket_tests = os.getenv("SHUFFL_ALLOW_SOCKET_TESTS", "0").lower() in {"1", "true", "yes"}
        attempts = 3 if allow_socket_tests else 1
        timeout_seconds = 10 if allow_socket_tests else 1.5
        for _ in range(attempts):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                probe.bind(("127.0.0.1", 0))
                candidates.append(int(probe.getsockname()[1]))

        last_details = ""
        for port in dict.fromkeys(candidates):
            cls._base_url = f"http://127.0.0.1:{port}"
            cls._process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
                cwd=str(BACKEND_ROOT), env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            )
            deadline = time.monotonic() + timeout_seconds
            while time.monotonic() < deadline:
                if cls._process.poll() is not None:
                    last_details = cls._process.stderr.read().decode("utf-8", "replace")[-2000:]
                    break
                try:
                    with urllib.request.urlopen(f"{cls._base_url}/health", timeout=0.5) as response:
                        if response.status == 200:
                            return
                except (OSError, urllib.error.URLError):
                    time.sleep(0.1)
            if cls._process.poll() is None:
                cls._process.kill()
                cls._process.wait(timeout=3)

        if not allow_socket_tests:
            cls._socket_unavailable = True
            pytest.skip("Loopback ASGI test server is unavailable in this environment; set SHUFFL_ALLOW_SOCKET_TESTS=1 to run socket-bound API contract tests.")
        detail = f"\n{last_details}" if last_details else ""
        raise RuntimeError(f"Test API server did not become healthy on any candidate port.{detail}")

    def request(self, method: str, url: str, **kwargs):
        self._ensure_server()
        target = urllib.parse.urljoin(self._base_url, url)
        params = kwargs.get("params")
        if params:
            target += ("&" if "?" in target else "?") + urllib.parse.urlencode(params)
        body = None
        if "json" in kwargs:
            body = json.dumps(kwargs["json"]).encode("utf-8")
        request = urllib.request.Request(target, data=body, method=method.upper())
        if body is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return _Response(response.status, response.read())
        except urllib.error.HTTPError as error:
            return _Response(error.code, error.read())

    def get(self, url: str, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.request("POST", url, **kwargs)

    def patch(self, url: str, **kwargs):
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs):
        return self.request("DELETE", url, **kwargs)


import fastapi.testclient
fastapi.testclient.TestClient = SyncASGITestClient


@atexit.register
def _stop_test_server():
    process = SyncASGITestClient._process
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()


