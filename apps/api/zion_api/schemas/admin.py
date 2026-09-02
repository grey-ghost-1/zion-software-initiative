"""Admin-only demonstration schemas."""

from __future__ import annotations

from pydantic import BaseModel


class OrganizationMember(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str


class OrganizationMembersResponse(BaseModel):
    organization_slug: str
    organization_name: str
    members: list[OrganizationMember]
