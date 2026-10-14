"""Password hashing and opaque session-token helpers.

Session tokens are random, high-entropy strings. Only a SHA-256 hash of each
token is persisted, so a database read alone cannot be replayed as a bearer
token, and no cryptographic secret needs to be managed for verification.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt

_TOKEN_NBYTES = 32


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password for storage."""

    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""

    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("ascii"))
    except ValueError:
        return False


def generate_session_token() -> tuple[str, str]:
    """Generate a new opaque session token.

    Returns ``(raw_token, token_hash)``. Only ``raw_token`` is ever returned to
    a client; only ``token_hash`` is persisted.
    """

    raw_token = secrets.token_urlsafe(_TOKEN_NBYTES)
    return raw_token, hash_token(raw_token)


def hash_token(raw_token: str) -> str:
    """Hash a raw bearer token for lookup/storage."""

    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def session_expiry(ttl_minutes: int) -> datetime:
    """Compute the UTC expiry timestamp for a newly issued session token."""

    return datetime.now(UTC) + timedelta(minutes=ttl_minutes)


def utcnow() -> datetime:
    """Return the current UTC time (single seam for test determinism)."""

    return datetime.now(UTC)


def ensure_aware_utc(value: datetime) -> datetime:
    """Normalize a datetime read back from the database to be UTC-aware.

    SQLite (used in tests) does not preserve timezone info: a value stored as
    UTC comes back naive. Every datetime this application persists is always
    UTC, so a naive value can be safely assumed to already be UTC.
    """

    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
