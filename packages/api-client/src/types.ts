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

/* ----------------------------- Haven contracts ---------------------------- */

export type HavenConcernCategory =
  | "fever_or_flu"
  | "cough_or_cold"
  | "stomach_trouble"
  | "minor_injury"
  | "medication_instructions"
  | "stress_or_anxiety"
  | "low_mood"
  | "sleep_trouble"
  | "cost_or_coverage"
  | "general_question";

export type HavenConcernDuration =
  | "under_one_day"
  | "one_to_three_days"
  | "four_to_seven_days"
  | "over_one_week";

export type HavenSeverity = "mild" | "moderate" | "severe";

export type HavenRoutingOutcome =
  | "emergency_now"
  | "crisis_support_now"
  | "clinician_soon"
  | "mental_health_support"
  | "low_cost_care_routing"
  | "self_care_education";

export type HavenPlanStatus = "open" | "reviewed" | "closed";

export type HavenReviewReasonCode =
  | "routing_confirmed"
  | "routing_too_cautious"
  | "routing_not_cautious_enough"
  | "resource_link_problem"
  | "demo_walkthrough_complete";

export interface HavenNavigationRequest {
  concern_category: HavenConcernCategory;
  duration: HavenConcernDuration;
  severity: HavenSeverity;
  immediate_danger?: boolean;
  self_harm_risk?: boolean;
  /** Optional short synthetic text (max 280 chars); never stored by the API. */
  concern_text?: string;
}

export interface HavenEmergencyGuidance {
  active: boolean;
  kind: "emergency_911" | "crisis_988" | null;
  headline: string | null;
  steps: string[];
  no_monitoring_note: string;
}

export interface HavenResource {
  slug: string;
  name: string;
  description: string;
  url: string;
  kind: "crisis_support" | "treatment_locator" | "low_cost_care" | "health_education";
  jurisdiction: string;
  provenance: "federal_agency" | "nonprofit_official" | "synthetic";
  source_mode: "live_official" | "synthetic_demo";
  /** ISO 8601 date strings, as serialized by the API. */
  reviewed_on: string;
  retrieved_on: string;
  review_valid_until: string;
  freshness: "current" | "needs_review";
}

export interface HavenResourceListResponse {
  resources: HavenResource[];
}

export interface HavenGuidanceCard {
  slug: string;
  category: HavenConcernCategory;
  title: string;
  original_text: string;
  plain_text: string;
  source_name: string;
  source_url: string;
  jurisdiction: string;
  reviewed_on: string;
}

export interface HavenGuidanceCardListResponse {
  cards: HavenGuidanceCard[];
}

export interface HavenNavigationResponse {
  synthetic: boolean;
  stored: boolean;
  emergency: HavenEmergencyGuidance;
  outcome: HavenRoutingOutcome;
  next_steps: string[];
  resources: HavenResource[];
  guidance_cards: HavenGuidanceCard[];
  disclaimer: string;
}

export interface HavenPlan {
  id: string;
  organization_slug: string;
  synthetic: boolean;
  concern_category: HavenConcernCategory;
  duration: HavenConcernDuration;
  severity: HavenSeverity;
  immediate_danger: boolean;
  self_harm_risk: boolean;
  crisis_language_detected: boolean;
  routed_outcome: HavenRoutingOutcome;
  status: HavenPlanStatus;
  review_reason_code: HavenReviewReasonCode | null;
  created_at: string;
  reviewed_at: string | null;
  closed_at: string | null;
}

export interface HavenPlanCreateResponse {
  plan: HavenPlan;
  navigation: HavenNavigationResponse;
}

export interface HavenPlanListResponse {
  organization_slug: string;
  plans: HavenPlan[];
}

export interface HavenPlanReviewRequest {
  reason_code: HavenReviewReasonCode;
}

export interface HavenPlanReviewResponse {
  plan: HavenPlan;
}

export interface HavenPlanCloseResponse {
  plan: HavenPlan;
}
