"""FastAPI dependencies for authentication, roles, and organization isolation."""

from __future__ import annotations

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.orm import Session

from zion_api.core.errors import (
    InvalidOrExpiredTokenError,
    OrganizationNotFoundError,
    RoleDeniedError,
)
from zion_api.core.security import ensure_aware_utc, hash_token, utcnow
from zion_api.db.session import get_db
from zion_api.models.auth_token import AuthToken
from zion_api.models.enums import Role
from zion_api.models.membership import Membership
from zion_api.models.organization import Organization
from zion_api.models.user import User


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise InvalidOrExpiredTokenError("A bearer token is required.")
    return authorization.split(" ", 1)[1].strip()


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the caller's user from a valid, unexpired, unrevoked token."""

    raw_token = _extract_bearer_token(authorization)
    token_hash = hash_token(raw_token)

    token = db.scalar(select(AuthToken).where(AuthToken.token_hash == token_hash))
    if (
        token is None
        or token.revoked_at is not None
        or ensure_aware_utc(token.expires_at) <= utcnow()
    ):
        raise InvalidOrExpiredTokenError("The bearer token is invalid or has expired.")

    user = db.get(User, token.user_id)
    if user is None or not user.is_active:
        raise InvalidOrExpiredTokenError("The bearer token is invalid or has expired.")
    return user


def get_membership_for_org(
    org_slug: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> tuple[Organization, Membership]:
    """Resolve the caller's membership in ``org_slug``.

    Returns an identical 404 whether the organization does not exist or the
    caller simply is not a member of it, so a caller cannot use this endpoint
    to enumerate organizations they cannot access.
    """

    organization = db.scalar(select(Organization).where(Organization.slug == org_slug))
    if organization is None:
        raise OrganizationNotFoundError("The organization was not found.")

    membership = db.scalar(
        select(Membership).where(
            Membership.organization_id == organization.id,
            Membership.user_id == current_user.id,
        )
    )
    if membership is None:
        raise OrganizationNotFoundError("The organization was not found.")

    return organization, membership


def require_admin(
    org_membership: tuple[Organization, Membership] = Depends(get_membership_for_org),
) -> tuple[Organization, Membership]:
    """Require an admin role within the resolved organization."""

    _, membership = org_membership
    if membership.role != Role.ADMIN:
        raise RoleDeniedError("This action requires the admin role in this organization.")
    return org_membership
