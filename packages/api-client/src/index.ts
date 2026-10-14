import { ZionApiError } from "./errors";
import type {
  ApiErrorBody,
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
  LivenessResponse,
  LoginRequest,
  LoginResponse,
  MembershipSummary,
  MeResponse,
  OrganizationMember,
  OrganizationMembersResponse,
  ReadinessResponse,
} from "./types";

export interface ZionApiClientOptions {
  /** e.g. "http://localhost:8000" — no trailing slash required. */
  baseUrl: string;
  /** Override for tests; defaults to the global `fetch`. */
  fetch?: typeof fetch;
}

interface RequestOptions {
  body?: unknown;
  accessToken?: string;
  /** When true, the parsed body is returned as-is even for non-2xx responses. */
  neverThrows?: boolean;
}

/**
 * A small, fully typed client for the Zion API endpoints implemented in this
 * foundation layer only: health, login, the caller's own profile, and the
 * one admin-only demonstration endpoint. Extend it only alongside a real,
 * implemented API endpoint — never speculatively.
 */
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

  /** Resolves with the readiness body even when the API reports HTTP 503. */
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
