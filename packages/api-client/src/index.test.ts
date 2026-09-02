import { describe, expect, it, vi } from "vitest";
import { ZionApiClient, ZionApiError } from "./index";

function jsonResponse(body: unknown, init: { status?: number } = {}): Response {
  return new Response(JSON.stringify(body), {
    status: init.status ?? 200,
    headers: { "Content-Type": "application/json" },
  });
}

describe("ZionApiClient", () => {
  it("trims a trailing slash from the base URL", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ status: "ok" }));
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000/", fetch: fetchMock });

    await client.getLiveness();

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/health/live",
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("returns the readiness body even when the API reports HTTP 503", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(
        jsonResponse({ status: "degraded", ready: false, detail: "not reachable" }, { status: 503 }),
      );
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    const result = await client.getReadiness();

    expect(result).toEqual({ status: "degraded", ready: false, detail: "not reachable" });
  });

  it("sends the JSON login body and returns the parsed response", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({ access_token: "abc", token_type: "bearer", expires_at: "2026-01-01T00:00:00Z" }),
    );
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    const result = await client.login({ email: "a@b.com", password: "secret" });

    expect(result.access_token).toBe("abc");
    const [, requestInit] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(requestInit.body).toBe(JSON.stringify({ email: "a@b.com", password: "secret" }));
    expect((requestInit.headers as Record<string, string>)["Content-Type"]).toBe("application/json");
  });

  it("attaches a bearer token for authenticated requests", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({ id: "1", email: "a@b.com", full_name: "A B", memberships: [] }),
    );
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    await client.getMe("token-123");

    const [, requestInit] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect((requestInit.headers as Record<string, string>).Authorization).toBe("Bearer token-123");
  });

  it("throws a ZionApiError carrying the code and request id on failure", async () => {
    const fetchMock = vi.fn().mockImplementation(() =>
      Promise.resolve(
        jsonResponse(
          { error: { code: "invalid_credentials", message: "bad", request_id: "req-1" } },
          { status: 401 },
        ),
      ),
    );
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    await expect(client.login({ email: "a@b.com", password: "wrong" })).rejects.toMatchObject({
      code: "invalid_credentials",
      status: 401,
      requestId: "req-1",
    });
    await expect(client.login({ email: "a@b.com", password: "wrong" })).rejects.toBeInstanceOf(
      ZionApiError,
    );
  });

  it("scopes admin member requests to the encoded organization slug", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({ organization_slug: "zion-demo", organization_name: "Zion Demo", members: [] }),
    );
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    await client.getOrganizationMembers("zion demo/alt", "token-123");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/admin/organizations/zion%20demo%2Falt/members",
      expect.anything(),
    );
  });

  it("keeps Harbor workflow paths and bodies aligned with the API contract", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({
          id: "need-1",
          request_ref: "DEMO-CLIENT-1",
          category: "food",
          zone: "central",
          quantity: 2,
          eligibility: "open_access",
          accessibility_requirement: "none",
          urgency: "standard",
          status: "submitted",
          triage_decision: null,
          triage_reason: null,
          created_at: "2026-09-01T00:00:00Z",
          synthetic: true,
        }),
      )
      .mockResolvedValueOnce(
        jsonResponse({
          id: "plan-1",
          need_id: "need-1",
          request_ref: "DEMO-CLIENT-1",
          resource_id: "resource-1",
          resource_name: "Synthetic resource",
          resource_zone: "central",
          category: "food",
          quantity: 2,
          volunteer_code: "VOL-1",
          status: "approved",
          proposed_at: "2026-09-01T00:00:00Z",
          approved_at: "2026-09-01T00:01:00Z",
          fulfilled_at: null,
          synthetic: true,
        }),
      );
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });
    const payload = {
      request_ref: "DEMO-CLIENT-1",
      category: "food" as const,
      zone: "central" as const,
      quantity: 2,
      eligibility: "open_access" as const,
      accessibility_requirement: "none" as const,
      urgency: "standard" as const,
    };

    await client.createHarborNeed("zion demo", payload, "token-123");
    await client.approveHarborPlan("zion demo", "plan/1", "token-123");

    expect(fetchMock.mock.calls[0]?.[0]).toBe(
      "http://localhost:8000/harbor/zion%20demo/needs",
    );
    expect((fetchMock.mock.calls[0]?.[1] as RequestInit).body).toBe(JSON.stringify(payload));
    expect(fetchMock.mock.calls[1]?.[0]).toBe(
      "http://localhost:8000/harbor/zion%20demo/plans/plan%2F1/approve",
    );
  });

  it("requires the coordinator-selected volunteer in a Harbor proposal body", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        id: "plan-1",
        need_id: "need-1",
        request_ref: "DEMO-CLIENT-1",
        resource_id: "resource-1",
        resource_name: "Synthetic resource",
        resource_zone: "central",
        category: "food",
        quantity: 2,
        volunteer_code: "VOL-1",
        status: "proposed",
        proposed_at: "2026-09-01T00:00:00Z",
        approved_at: null,
        fulfilled_at: null,
        synthetic: true,
      }),
    );
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    await client.proposeHarborPlan(
      "zion-demo",
      "need-1",
      { resource_id: "resource-1", volunteer_availability_id: "volunteer-1" },
      "token",
    );

    expect((fetchMock.mock.calls[0]?.[1] as RequestInit).body).toBe(
      JSON.stringify({
        resource_id: "resource-1",
        volunteer_availability_id: "volunteer-1",
      }),
    );
  });
});
