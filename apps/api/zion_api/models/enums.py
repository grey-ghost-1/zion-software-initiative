"""Shared enumerations for the Zion schema."""

from __future__ import annotations

import enum


class Role(enum.StrEnum):
    """Reusable membership roles.

    Only ``admin`` is enforced by any endpoint in this foundation layer. The
    remaining roles exist so later product modules can reuse one shared role
    vocabulary instead of each defining its own.
    """

    VISITOR = "visitor"
    COORDINATOR = "coordinator"
    NAVIGATOR = "navigator"
    VOLUNTEER = "volunteer"
    ADMIN = "admin"
