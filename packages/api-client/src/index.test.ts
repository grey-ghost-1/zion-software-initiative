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
