"""Auth and profile schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class MembershipSummary(BaseModel):
    organization_slug: str
    organization_name: str
    role: str


class MeResponse(BaseModel):
    id: str
    email: str
    full_name: str
    memberships: list[MembershipSummary]
