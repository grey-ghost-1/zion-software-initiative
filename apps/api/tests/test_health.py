import socket
import subprocess
import sys
import time
from http.client import HTTPResponse
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from fastapi.testclient import TestClient

from zion_api.main import app

client = TestClient(app)
API_ROOT = Path(__file__).resolve().parents[1]


def test_liveness_contract_is_minimal_and_non_leaking() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert set(response.headers).isdisjoint({"server", "x-powered-by"})


def test_readiness_truthfully_reports_foundation_only_status() -> None:
    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "foundation_only",
        "ready": False,
        "detail": "Production dependencies and product modules are not configured.",
    }

    responses = app.openapi()["paths"]["/health/ready"]["get"]["responses"]
    assert set(responses) == {"503"}


def test_live_server_disables_implementation_header() -> None:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "zion_api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--no-server-header",
        ],
        cwd=API_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    response: HTTPResponse | None = None
    try:
        for _ in range(40):
            try:
                response = urlopen(f"http://127.0.0.1:{port}/health/live", timeout=1)
                break
            except URLError:
                time.sleep(0.1)

        assert response is not None
        assert response.status == 200
        assert response.headers.get("server") is None
    finally:
        if response is not None:
            response.close()
        process.terminate()
        process.wait(timeout=5)
