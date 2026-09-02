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

/* --- Beacon demonstration workflow (mirrors zion_api/schemas/beacon.py) --- */

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
