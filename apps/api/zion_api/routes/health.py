"""Health contracts: a minimal liveness probe and a truthful readiness probe."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from zion_api.db.session import get_db

router = APIRouter(prefix="/health", tags=["health"])


class LivenessResponse(BaseModel):
    """Stable liveness response without build or environment details."""

    status: Literal["ok"] = "ok"


class ReadinessResponse(BaseModel):
    """Truthful readiness response reflecting real database connectivity."""

    status: Literal["ok", "degraded"]
    ready: bool
    detail: str


@router.get("/live", response_model=LivenessResponse)
def liveness() -> LivenessResponse:
    """Report only whether the API process can answer requests."""

    return LivenessResponse()


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={
        status.HTTP_200_OK: {"description": "The database is reachable."},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"description": "The database is not reachable."},
    },
)
def readiness(response: Response, db: Session = Depends(get_db)) -> ReadinessResponse:
    """Check real database connectivity and report it truthfully.

    This intentionally does not report readiness for domain/product modules
    that do not exist yet in this foundation layer.
    """

    try:
        db.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 - any connectivity failure means not ready
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(
            status="degraded", ready=False, detail="The database is not reachable."
        )
    response.status_code = status.HTTP_200_OK
    return ReadinessResponse(
        status="ok", ready=True, detail="The database connectivity check succeeded."
    )
