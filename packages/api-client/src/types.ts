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

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    request_id: string;
  };
}

export type NeedCategory = "food" | "temporary_shelter" | "essential_supplies" | "transportation";
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

export interface BeaconToolSpec {
  name: string;
  description: string;
  input_type: string;
  output_type: string;
  timeout_seconds: number;
  max_attempts: number;
}

export interface BeaconWorkflowStep {
  step_key: string;
  tool: string;
}

export interface BeaconCapabilitiesResponse {
  workflow_key: string;
  workflow_version: string;
  workflow_name: string;
  policy_version: string;
  steps: BeaconWorkflowStep[];
  tools: BeaconToolSpec[];
  scenarios: string[];
  guardrails: string[];
  disclosure: string;
}

export type BeaconScenario =
  | "default"
  | "transient-timeout"
  | "stale-data"
  | "invalid-crs"
  | "malformed-geometry"
  | "impossible-coordinates"
  | "antimeridian"
  | "injection"
  | "sensitive-data";

export interface BeaconStartRunRequest {
  idempotency_key: string;
  scenario?: BeaconScenario;
}

export interface BeaconRunStep {
  seq: number;
  step_key: string;
  tool_name: string;
  attempt: number;
  status: string;
  detail: Record<string, unknown>;
  created_at: string;
}

export interface BeaconPolicyCheck {
  check: string;
  passed: boolean;
  detail: Record<string, unknown>;
}

export interface BeaconProvenance {
  fixture_id: string;
  source_label: string;
  synthetic: boolean;
  license_note: string;
  checksum_sha256: string;
  effective_at: string;
  retrieved_at: string;
}

export interface BeaconAllocationLine {
  zone_id: string;
  item: string;
  quantity: number;
  reason: string;
}

export interface BeaconProposal {
  id: string;
  status: string;
  lines: BeaconAllocationLine[];
  unmet_demand: BeaconAllocationLine[];
  decided_at: string | null;
  decision_note: string | null;
}

export interface BeaconRunSummary {
  id: string;
  workflow_key: string;
  workflow_version: string;
  policy_version: string;
  scenario: string;
  fixture_id: string;
  status: string;
  idempotency_key: string;
  replay_count: number;
  created_at: string;
}

export interface BeaconRunDetail extends BeaconRunSummary {
  steps: BeaconRunStep[];
  policy_results: BeaconPolicyCheck[];
  provenance: BeaconProvenance[];
  proposal: BeaconProposal | null;
  metrics: Record<string, unknown>;
  disclosures: string[];
}

export interface BeaconStartRunResponse {
  created: boolean;
  run: BeaconRunDetail;
}

export interface BeaconRunListResponse {
  organization_slug: string;
  runs: BeaconRunSummary[];
}

export interface BeaconApprovalRequest {
  decision: "approve" | "reject";
  note?: string | null;
}
