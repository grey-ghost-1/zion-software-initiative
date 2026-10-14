"""Admin-only demonstration endpoint.

This exists to demonstrate server-side RBAC and organization isolation end to
end; it is not a product feature. It lists the members of one organization,
visible only to an admin of that same organization.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from zion_api.db.session import get_db
from zion_api.deps import require_admin
from zion_api.models.membership import Membership
from zion_api.models.organization import Organization
from zion_api.models.user import User
from zion_api.schemas.admin import OrganizationMember, OrganizationMembersResponse
from zion_api.services.audit import record_audit_event

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/organizations/{org_slug}/members",
    response_model=OrganizationMembersResponse,
)
def list_organization_members(
    org_membership: tuple[Organization, Membership] = Depends(require_admin),
    db: Session = Depends(get_db),
) -> OrganizationMembersResponse:
    """List every member of one organization. Admin-only, organization-scoped."""

    organization, membership = org_membership

    rows = db.execute(
        select(Membership, User)
        .join(User, User.id == Membership.user_id)
        .where(Membership.organization_id == organization.id)
        .order_by(User.email)
    ).all()

    members = [
        OrganizationMember(
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=row_membership.role.value,
        )
        for row_membership, user in rows
    ]

    record_audit_event(
        db,
        action="admin.members_viewed",
        actor_user_id=membership.user_id,
        organization_id=organization.id,
        subject_type="organization",
        subject_id=organization.id,
        context={"member_count": len(members)},
    )
    db.commit()

    return OrganizationMembersResponse(
        organization_slug=organization.slug,
        organization_name=organization.name,
        members=members,
    )
