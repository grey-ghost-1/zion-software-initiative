"""Password hashing and token helper unit tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from zion_api.core.security import (
    ensure_aware_utc,
    generate_session_token,
    hash_password,
    hash_token,
    session_expiry,
    verify_password,
)


def test_hash_password_never_stores_the_plaintext() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert password_hash != "correct horse battery staple"
    assert verify_password("correct horse battery staple", password_hash)


def test_verify_password_rejects_the_wrong_password() -> None:
    password_hash = hash_password("correct horse battery staple")

    assert not verify_password("wrong password", password_hash)


def test_verify_password_rejects_malformed_hashes_without_raising() -> None:
    assert not verify_password("anything", "not-a-real-bcrypt-hash")


def test_generate_session_token_returns_distinct_raw_and_hashed_values() -> None:
    raw_token, token_hash = generate_session_token()

    assert raw_token != token_hash
    assert token_hash == hash_token(raw_token)
    # A second token must never collide with the first.
    other_raw, other_hash = generate_session_token()
    assert other_raw != raw_token
    assert other_hash != token_hash


def test_session_expiry_is_in_the_future_by_the_configured_ttl() -> None:
    expiry = session_expiry(ttl_minutes=30)

    assert expiry > datetime.now(UTC)
    assert expiry < datetime.now(UTC) + timedelta(minutes=31)


def test_ensure_aware_utc_normalizes_naive_datetimes() -> None:
    naive = datetime(2026, 1, 1, 12, 0, 0)

    aware = ensure_aware_utc(naive)

    assert aware.tzinfo is UTC
    assert aware.hour == 12
