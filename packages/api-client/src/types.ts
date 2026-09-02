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

export type NeedCategory =
  | "food"
  | "temporary_shelter"
  | "essential_supplies"
  | "transportation";
export type HarborZone = "north" | "central" | "south";
export type Eligibility = "open_access" | "coordinator_referral";
export type AccessibilityRequirement = "none" | "step_free";
export type AccessibilityStatus = "step_free" | "limited" | "unknown";
export type NeedUrgency = "standard" | "time_sensitive";
export type NeedStatus =
  | "submitted"
  | "triaged"
  | "deferred"
  | "proposed"
  | "approved"
  | "fulfilled";
export type TriageDecision = "ready" | "defer";
export type TriageReason =
  | "match_explanation_reviewed"
  | "capacity_recheck_required"
  | "synthetic_scenario_hold"
  | "coordinator_override";
export type PlanStatus = "proposed" | "approved" | "fulfilled";

export interface HarborNeedCreate {
  request_ref: string;
  category: NeedCategory;
  zone: HarborZone;
  quantity: number;
  eligibility: Eligibility;
  accessibility_requirement: AccessibilityRequirement;
  urgency: NeedUrgency;
}

export interface HarborNeed extends HarborNeedCreate {
  id: string;
  status: NeedStatus;
  triage_decision: TriageDecision | null;
  triage_reason: TriageReason | null;
  created_at: string;
  synthetic: true;
}

export interface HarborNeedList {
  items: HarborNeed[];
  synthetic_disclosure: string;
}

export interface HarborCapacity {
  total_units: number;
  reserved_units: number;
  fulfilled_units: number;
  available_units: number | null;
  freshness: "current" | "stale" | "unknown";
}

export interface HarborResource {
  id: string;
  code: string;
  name: string;
  category: NeedCategory;
  zone: HarborZone;
  eligibility: Eligibility;
  accessibility: AccessibilityStatus;
  status: "open" | "closed";
  capacity: HarborCapacity | null;
  synthetic: true;
}

export interface HarborResourceList {
  items: HarborResource[];
  synthetic_disclosure: string;
}

export interface ScoreComponent {
  rule: string;
  points: number;
  explanation: string;
}

export interface HarborMatch {
  resource: HarborResource;
  score: number | null;
  score_components: ScoreComponent[];
  rejected_reasons: string[];
  uncertainty: string[];
}

export interface HarborMatchResponse {
  need: HarborNeed;
  matches: HarborMatch[];
  rejected: HarborMatch[];
  scoring_notice: string;
  protected_traits_used: false;
}

export interface HarborTriageRequest {
  decision: TriageDecision;
  reason: TriageReason;
  selected_resource_id?: string;
}

export interface HarborPlanProposal {
  resource_id: string;
  volunteer_availability_id: string;
}

export interface HarborVolunteerAvailability {
  id: string;
  code: string;
  zone: HarborZone;
  category: NeedCategory;
  available: boolean;
}

export interface HarborVolunteerAvailabilityList {
  items: HarborVolunteerAvailability[];
  selection_notice: string;
}

export interface HarborPlan {
  id: string;
  need_id: string;
  request_ref: string;
  resource_id: string;
  resource_name: string;
  resource_zone: HarborZone;
  category: NeedCategory;
  quantity: number;
  volunteer_code: string;
  status: PlanStatus;
  proposed_at: string;
  approved_at: string | null;
  fulfilled_at: string | null;
  synthetic: true;
}

export interface HarborVolunteerPlanList {
  items: HarborPlan[];
  scope_notice: string;
}

export interface HarborAuditItem {
  id: string;
  occurred_at: string;
  action: string;
  context: Record<string, unknown>;
}

export interface HarborAuditTimeline {
  need_id: string;
  items: HarborAuditItem[];
}

export interface HarborMetrics {
  total_requests: number;
  submitted_requests: number;
  active_plans: number;
  awaiting_approval: number;
  fulfilled_requests: number;
  currently_available_resources: number;
  reserved_units: number;
  fulfilled_units: number;
  synthetic_disclosure: string;
}
