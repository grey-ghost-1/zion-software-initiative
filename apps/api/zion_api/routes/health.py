"""Minimal health contracts for the foundation service."""

from typing import Literal

from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class LivenessResponse(BaseModel):
    """Stable liveness response without build or environment details."""

    status: Literal["ok"] = "ok"


class ReadinessResponse(BaseModel):
    """Truthful readiness response for the foundation-only service."""

    status: Literal["foundation_only"] = "foundation_only"
    ready: Literal[False] = False
    detail: str = "Production dependencies and product modules are not configured."


@router.get("/live", response_model=LivenessResponse)
def liveness() -> LivenessResponse:
    """Report only whether the API process can answer requests."""

    return LivenessResponse()


@router.get(
    "/ready",
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    response_model=ReadinessResponse,
)
def readiness() -> ReadinessResponse:
    """Remain unready until later layers configure real dependencies."""

    return ReadinessResponse()
