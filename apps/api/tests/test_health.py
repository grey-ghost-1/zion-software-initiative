"""Health contract tests: liveness, truthful readiness, and no header leakage."""

import socket
import subprocess
import sys
import time
from http.client import HTTPResponse
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from fastapi.testclient import TestClient

API_ROOT = Path(__file__).resolve().parents[1]


def test_liveness_contract_is_minimal_and_non_leaking(client: TestClient) -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert set(response.headers).isdisjoint({"server", "x-powered-by"})


def test_readiness_reports_ready_when_database_is_reachable(client: TestClient) -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "ready": True,
        "detail": "The database connectivity check succeeded.",
    }


def test_readiness_reports_degraded_when_database_is_unreachable() -> None:
    from zion_api.db.session import get_db
    from zion_api.main import app

    class _BrokenSession:
        def execute(self, *_args: object, **_kwargs: object) -> None:
            raise RuntimeError("database unavailable")

    def override_get_db() -> object:
        yield _BrokenSession()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as broken_client:
            response = broken_client.get("/health/ready")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "ready": False,
        "detail": "The database is not reachable.",
    }


def test_every_response_carries_a_request_id(client: TestClient) -> None:
    response = client.get("/health/live")

    assert "x-request-id" in response.headers
    assert len(response.headers["x-request-id"]) == 32


def test_client_supplied_request_id_is_ignored(client: TestClient) -> None:
    response = client.get("/health/live", headers={"X-Request-ID": "attacker-controlled"})

    assert response.headers["x-request-id"] != "attacker-controlled"


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
