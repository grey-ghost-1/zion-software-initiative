import { ZionApiError } from "./errors";
import type {
  ApiErrorBody,
  HarborAuditTimeline,
  HarborMatchResponse,
  HarborMetrics,
  HarborNeed,
  HarborNeedCreate,
  HarborNeedList,
  HarborPlan,
  HarborPlanProposal,
  HarborResource,
  HarborResourceList,
  HarborTriageRequest,
  HarborVolunteerAvailabilityList,
  HarborVolunteerPlanList,
  HavenGuidanceCardListResponse,
  HavenNavigationRequest,
  HavenNavigationResponse,
  HavenPlanCloseResponse,
  HavenPlanCreateResponse,
  HavenPlanListResponse,
  HavenPlanReviewRequest,
  HavenPlanReviewResponse,
  HavenResourceListResponse,
  LivenessResponse,
  LoginRequest,
  LoginResponse,
  MeResponse,
  OrganizationMembersResponse,
  ReadinessResponse,
} from "./types";

export type { ApiErrorBody } from "./types";
export { ZionApiError } from "./errors";
export type {
  AccessibilityRequirement,
  AccessibilityStatus,
  Eligibility,
  HarborAuditItem,
  HarborAuditTimeline,
  HarborCapacity,
  HarborMatch,
  HarborMatchResponse,
  HarborMetrics,
  HarborNeed,
  HarborNeedCreate,
  HarborNeedList,
  HarborPlan,
  HarborPlanProposal,
  HarborResource,
  HarborResourceList,
  HarborTriageRequest,
  HarborVolunteerAvailability,
  HarborVolunteerAvailabilityList,
  HarborVolunteerPlanList,
  HarborZone,
  HavenConcernCategory,
  HavenConcernDuration,
  HavenEmergencyGuidance,
  HavenGuidanceCard,
  HavenGuidanceCardListResponse,
  HavenNavigationRequest,
  HavenNavigationResponse,
  HavenPlan,
  HavenPlanCloseResponse,
  HavenPlanCreateResponse,
  HavenPlanListResponse,
  HavenPlanReviewRequest,
  HavenPlanReviewResponse,
  HavenPlanStatus,
  HavenResource,
  HavenResourceListResponse,
  HavenReviewReasonCode,
  HavenRoutingOutcome,
  HavenSeverity,
  LivenessResponse,
  LoginRequest,
  LoginResponse,
  MembershipSummary,
  MeResponse,
  NeedCategory,
  NeedStatus,
  NeedUrgency,
  OrganizationMember,
  OrganizationMembersResponse,
  PlanStatus,
  ReadinessResponse,
  ScoreComponent,
  TriageDecision,
  TriageReason,
} from "./types";

export interface ZionApiClientOptions {
  baseUrl: string;
  fetch?: typeof fetch;
}

interface RequestOptions {
  body?: unknown;
  accessToken?: string;
  neverThrows?: boolean;
}

export class ZionApiClient {
  private readonly baseUrl: string;
  private readonly fetchImpl: typeof fetch;

  constructor(options: ZionApiClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/+$/, "");
    this.fetchImpl = options.fetch ?? fetch;
  }

  getLiveness(): Promise<LivenessResponse> {
    return this.request<LivenessResponse>("GET", "/health/live");
  }

  getReadiness(): Promise<ReadinessResponse> {
    return this.request<ReadinessResponse>("GET", "/health/ready", { neverThrows: true });
  }

  login(payload: LoginRequest): Promise<LoginResponse> {
    return this.request<LoginResponse>("POST", "/auth/login", { body: payload });
  }

  getMe(accessToken: string): Promise<MeResponse> {
    return this.request<MeResponse>("GET", "/me", { accessToken });
  }

  getOrganizationMembers(
    organizationSlug: string,
    accessToken: string,
  ): Promise<OrganizationMembersResponse> {
    return this.request<OrganizationMembersResponse>(
      "GET",
      `/admin/organizations/${encodeURIComponent(organizationSlug)}/members`,
      { accessToken },
    );
  }

  listHarborNeeds(organizationSlug: string, accessToken: string): Promise<HarborNeedList> {
    return this.request<HarborNeedList>(
      "GET",
      `/harbor/${encodeURIComponent(organizationSlug)}/needs`,
      { accessToken },
    );
  }

  getHarborNeed(
    organizationSlug: string,
    needId: string,
    accessToken: string,
  ): Promise<HarborNeed> {
    return this.request<HarborNeed>(
      "GET",
      `/harbor/${encodeURIComponent(organizationSlug)}/needs/${encodeURIComponent(needId)}`,
      { accessToken },
    );
  }

  createHarborNeed(
    organizationSlug: string,
    payload: HarborNeedCreate,
    accessToken: string,
  ): Promise<HarborNeed> {
    return this.request<HarborNeed>(
      "POST",
      `/harbor/${encodeURIComponent(organizationSlug)}/needs`,
      { body: payload, accessToken },
    );
  }

  listHarborResources(
    organizationSlug: string,
    accessToken: string,
  ): Promise<HarborResourceList> {
    return this.request<HarborResourceList>(
      "GET",
      `/harbor/${encodeURIComponent(organizationSlug)}/resources`,
      { accessToken },
    );
  }

  getHarborResource(
    organizationSlug: string,
    resourceId: string,
    accessToken: string,
  ): Promise<HarborResource> {
    return this.request<HarborResource>(
      "GET",
      `/harbor/${encodeURIComponent(organizationSlug)}/resources/${encodeURIComponent(resourceId)}`,
      { accessToken },
    );
  }

  getHarborMatches(
    organizationSlug: string,
    needId: string,
    accessToken: string,
  ): Promise<HarborMatchResponse> {
    return this.request<HarborMatchResponse>(
      "GET",
      `/harbor/${encodeURIComponent(organizationSlug)}/needs/${encodeURIComponent(needId)}/matches`,
      { accessToken },
    );
  }

  triageHarborNeed(
    organizationSlug: string,
    needId: string,
    payload: HarborTriageRequest,
    accessToken: string,
  ): Promise<HarborNeed> {
    return this.request<HarborNeed>(
      "POST",
      `/harbor/${encodeURIComponent(organizationSlug)}/needs/${encodeURIComponent(needId)}/triage`,
      { body: payload, accessToken },
    );
  }

  proposeHarborPlan(
    organizationSlug: string,
    needId: string,
    payload: HarborPlanProposal,
    accessToken: string,
  ): Promise<HarborPlan> {
    return this.request<HarborPlan>(
      "POST",
      `/harbor/${encodeURIComponent(organizationSlug)}/needs/${encodeURIComponent(needId)}/plans`,
      { body: payload, accessToken },
    );
  }

  listHarborVolunteerAvailability(
    organizationSlug: string,
    accessToken: string,
  ): Promise<HarborVolunteerAvailabilityList> {
    return this.request<HarborVolunteerAvailabilityList>(
      "GET",
      `/harbor/${encodeURIComponent(organizationSlug)}/volunteer-availability`,
      { accessToken },
    );
  }

  approveHarborPlan(
    organizationSlug: string,
    planId: string,
    accessToken: string,
  ): Promise<HarborPlan> {
    return this.request<HarborPlan>(
      "POST",
      `/harbor/${encodeURIComponent(organizationSlug)}/plans/${encodeURIComponent(planId)}/approve`,
      { accessToken },
    );
  }

  fulfillHarborPlan(
    organizationSlug: string,
    planId: string,
    accessToken: string,
  ): Promise<HarborPlan> {
    return this.request<HarborPlan>(
      "POST",
      `/harbor/${encodeURIComponent(organizationSlug)}/plans/${encodeURIComponent(planId)}/fulfill`,
      { accessToken },
    );
  }

  listHarborVolunteerPlans(
    organizationSlug: string,
    accessToken: string,
  ): Promise<HarborVolunteerPlanList> {
    return this.request<HarborVolunteerPlanList>(
      "GET",
      `/harbor/${encodeURIComponent(organizationSlug)}/volunteer-plans`,
      { accessToken },
    );
  }

  getHarborAudit(
    organizationSlug: string,
    needId: string,
    accessToken: string,
  ): Promise<HarborAuditTimeline> {
    return this.request<HarborAuditTimeline>(
      "GET",
      `/harbor/${encodeURIComponent(organizationSlug)}/needs/${encodeURIComponent(needId)}/audit`,
      { accessToken },
    );
  }

  getHarborMetrics(
    organizationSlug: string,
    accessToken: string,
  ): Promise<HarborMetrics> {
    return this.request<HarborMetrics>(
      "GET",
      `/harbor/${encodeURIComponent(organizationSlug)}/metrics`,
      { accessToken },
    );
  }

  listHavenGuidanceCards(): Promise<HavenGuidanceCardListResponse> {
    return this.request<HavenGuidanceCardListResponse>("GET", "/haven/guidance-cards");
  }

  listHavenResources(): Promise<HavenResourceListResponse> {
    return this.request<HavenResourceListResponse>("GET", "/haven/resources");
  }

  submitHavenNavigation(payload: HavenNavigationRequest): Promise<HavenNavigationResponse> {
    return this.request<HavenNavigationResponse>("POST", "/haven/navigations", {
      body: payload,
    });
  }

  createHavenPlan(
    organizationSlug: string,
    payload: HavenNavigationRequest,
    accessToken: string,
  ): Promise<HavenPlanCreateResponse> {
    return this.request<HavenPlanCreateResponse>(
      "POST",
      `/haven/organizations/${encodeURIComponent(organizationSlug)}/plans`,
      { body: payload, accessToken },
    );
  }

  listHavenPlans(
    organizationSlug: string,
    accessToken: string,
  ): Promise<HavenPlanListResponse> {
    return this.request<HavenPlanListResponse>(
      "GET",
      `/haven/organizations/${encodeURIComponent(organizationSlug)}/plans`,
      { accessToken },
    );
  }

  reviewHavenPlan(
    organizationSlug: string,
    planId: string,
    payload: HavenPlanReviewRequest,
    accessToken: string,
  ): Promise<HavenPlanReviewResponse> {
    return this.request<HavenPlanReviewResponse>(
      "POST",
      `/haven/organizations/${encodeURIComponent(organizationSlug)}/plans/${encodeURIComponent(planId)}/review`,
      { body: payload, accessToken },
    );
  }

  closeHavenPlan(
    organizationSlug: string,
    planId: string,
    accessToken: string,
  ): Promise<HavenPlanCloseResponse> {
    return this.request<HavenPlanCloseResponse>(
      "POST",
      `/haven/organizations/${encodeURIComponent(organizationSlug)}/plans/${encodeURIComponent(planId)}/close`,
      { accessToken },
    );
  }

  private async request<T>(
    method: string,
    path: string,
    { body, accessToken, neverThrows }: RequestOptions = {},
  ): Promise<T> {
    const headers: Record<string, string> = {};
    if (body !== undefined) {
      headers["Content-Type"] = "application/json";
    }
    if (accessToken) {
      headers.Authorization = `Bearer ${accessToken}`;
    }

    const response = await this.fetchImpl(`${this.baseUrl}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });

    const data = (await response.json()) as unknown;

    if (!response.ok && !neverThrows) {
      throw new ZionApiError(response.status, data as ApiErrorBody);
    }

    return data as T;
  }
}
