"""Membership model linking a user to an organization with one reusable role."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from zion_api.db.base import Base
from zion_api.models.enums import Role

if TYPE_CHECKING:
    from zion_api.models.organization import Organization
    from zion_api.models.user import User


class Membership(Base):
    """One user's role within one organization.

    A user may belong to multiple organizations with different roles in
    each, which is what makes cross-organization isolation meaningful to
    test: an admin in one organization must not automatically gain any
    access in another.
    """

    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_membership_user_org"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[Role] = mapped_column(
        Enum(
            Role,
            native_enum=False,
            validate_strings=True,
            length=20,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped[User] = relationship(back_populates="memberships")
    organization: Mapped[Organization] = relationship(back_populates="memberships")
