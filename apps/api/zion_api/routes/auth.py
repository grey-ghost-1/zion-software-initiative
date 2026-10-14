"""Authentication endpoints: login and the caller's own profile."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from zion_api.core.config import get_settings
from zion_api.core.errors import InvalidCredentialsError
from zion_api.core.security import (
    generate_session_token,
    session_expiry,
    verify_password,
)
from zion_api.db.session import get_db
from zion_api.deps import get_current_user
from zion_api.models.auth_token import AuthToken
from zion_api.models.user import User
from zion_api.schemas.auth import LoginRequest, LoginResponse, MembershipSummary, MeResponse
from zion_api.services.audit import record_audit_event

router = APIRouter(tags=["auth"])


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """Authenticate with email and password and issue an expiring session token.

    The same generic error is returned whether the email is unknown or the
    password is wrong, so a caller cannot use this endpoint to enumerate
    registered emails.
    """

    user = db.scalar(select(User).where(User.email == payload.email.strip().lower()))
    if user is None or not user.is_active:
        raise InvalidCredentialsError("The email or password is incorrect.")
    if not verify_password(payload.password, user.password_hash):
        raise InvalidCredentialsError("The email or password is incorrect.")

    settings = get_settings()
    raw_token, token_hash = generate_session_token()
    expires_at = session_expiry(settings.session_token_ttl_minutes)

    db.add(AuthToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at))
    record_audit_event(
        db,
        action="auth.login",
        actor_user_id=user.id,
        subject_type="user",
        subject_id=user.id,
    )
    db.commit()

    return LoginResponse(access_token=raw_token, expires_at=expires_at)


@router.get("/me", response_model=MeResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> MeResponse:
    """Return the authenticated caller's own profile and organization roles."""

    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        memberships=[
            MembershipSummary(
                organization_slug=membership.organization.slug,
                organization_name=membership.organization.name,
                role=membership.role.value,
            )
            for membership in current_user.memberships
        ],
    )
