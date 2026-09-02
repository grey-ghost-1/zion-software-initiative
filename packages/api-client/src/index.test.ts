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
});

describe("ZionApiClient Haven endpoints", () => {
  const emergency = {
    active: false,
    kind: null,
    headline: null,
    steps: [],
    no_monitoring_note: "This demonstration does not monitor you.",
  };

  it("fetches curated guidance cards and resources from the public endpoints", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ cards: [] }))
      .mockResolvedValueOnce(jsonResponse({ resources: [] }));
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    await client.listHavenGuidanceCards();
    await client.listHavenResources();

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/haven/guidance-cards",
      expect.objectContaining({ method: "GET" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/haven/resources",
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("submits a bounded navigation request and parses the typed response", async () => {
    const body = {
      synthetic: true,
      stored: false,
      emergency: { ...emergency, active: true, kind: "crisis_988", headline: "988", steps: ["988"] },
      outcome: "crisis_support_now",
      next_steps: ["Call or text 988"],
      resources: [],
      guidance_cards: [],
      disclaimer: "Not a medical service.",
    };
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(body));
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    const result = await client.submitHavenNavigation({
      concern_category: "general_question",
      duration: "under_one_day",
      severity: "mild",
      self_harm_risk: true,
    });

    expect(result.emergency.kind).toBe("crisis_988");
    expect(result.stored).toBe(false);
    const [url, requestInit] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("http://localhost:8000/haven/navigations");
    expect(requestInit.method).toBe("POST");
    expect(JSON.parse(requestInit.body as string).self_harm_risk).toBe(true);
  });

  it("scopes plan lifecycle calls to the encoded organization and plan", async () => {
    const plan = {
      id: "plan 1",
      organization_slug: "zion-demo",
      synthetic: true,
      concern_category: "low_mood",
      duration: "over_one_week",
      severity: "moderate",
      immediate_danger: false,
      self_harm_risk: false,
      crisis_language_detected: false,
      routed_outcome: "mental_health_support",
      status: "reviewed",
      review_reason_code: "routing_confirmed",
      created_at: "2026-09-01T00:00:00Z",
      reviewed_at: "2026-09-01T00:05:00Z",
      closed_at: null,
    };
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(jsonResponse({ plan })));
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    const reviewed = await client.reviewHavenPlan(
      "zion-demo",
      "plan 1",
      { reason_code: "routing_confirmed" },
      "token-123",
    );
    await client.closeHavenPlan("zion-demo", "plan 1", "token-123");

    expect(reviewed.plan.review_reason_code).toBe("routing_confirmed");
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/haven/organizations/zion-demo/plans/plan%201/review",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/haven/organizations/zion-demo/plans/plan%201/close",
      expect.objectContaining({ method: "POST" }),
    );
    const [, reviewInit] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect((reviewInit.headers as Record<string, string>).Authorization).toBe("Bearer token-123");
  });

  it("surfaces the typed 503 error when Haven is degraded for non-crisis requests", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse(
        {
          error: {
            code: "haven_temporarily_unavailable",
            message: "Curated guidance is temporarily unavailable.",
            request_id: "req-9",
          },
        },
        { status: 503 },
      ),
    );
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    await expect(
      client.submitHavenNavigation({
        concern_category: "general_question",
        duration: "under_one_day",
        severity: "mild",
      }),
    ).rejects.toMatchObject({ code: "haven_temporarily_unavailable", status: 503 });
  });
});
