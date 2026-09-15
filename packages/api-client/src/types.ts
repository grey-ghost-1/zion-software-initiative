/** Typed request/response contracts mirroring the FastAPI Pydantic schemas. */

export interface LivenessResponse {
  status: "ok";
}

export interface ReadinessResponse {
  status: "ok" | "degraded";
  ready: boolean;
  detail: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  /** ISO 8601 timestamp string, as serialized by the API. */
  expires_at: string;
}

export interface MembershipSummary {
  organization_slug: string;
  organization_name: string;
  role: string;
}

export interface MeResponse {
  id: string;
  email: string;
  full_name: string;
  memberships: MembershipSummary[];
}

export interface OrganizationMember {
  user_id: string;
  email: string;
  full_name: string;
  role: string;
}

export interface OrganizationMembersResponse {
  organization_slug: string;
  organization_name: string;
  members: OrganizationMember[];
}

/** The stable typed error envelope every non-2xx JSON response uses. */
export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    request_id: string;
  };
}
