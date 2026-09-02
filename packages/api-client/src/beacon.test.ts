import { describe, expect, it, vi } from "vitest";
import { ZionApiClient, ZionApiError } from "./index";

function jsonResponse(body: unknown, init: { status?: number } = {}): Response {
  return new Response(JSON.stringify(body), {
    status: init.status ?? 200,
    headers: { "Content-Type": "application/json" },
  });
}

describe("ZionApiClient Beacon endpoints", () => {
  it("fetches capabilities without authentication", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        workflow_key: "coastal-storm-readiness",
        workflow_version: "1",
        workflow_name: "Coastal storm readiness (synthetic demonstration)",
        policy_version: "beacon-policy-v1",
        steps: [],
        tools: [],
        scenarios: ["default"],
        guardrails: [],
        disclosure: "Synthetic exploratory demonstration only.",
      }),
    );
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    const capabilities = await client.getBeaconCapabilities();

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/beacon/capabilities",
      expect.objectContaining({ method: "GET" }),
    );
    expect(capabilities.policy_version).toBe("beacon-policy-v1");
    const [, requestInit] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect((requestInit.headers as Record<string, string>).Authorization).toBeUndefined();
  });

  it("starts a run with an idempotency key and scenario", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({ created: true, run: { id: "run-1", status: "awaiting_approval" } }),
    );
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    const result = await client.startBeaconRun(
      "zion-demo",
      { idempotency_key: "key-1", scenario: "default" },
      "token-1",
    );

    expect(result.created).toBe(true);
    const [url, requestInit] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("http://localhost:8000/beacon/organizations/zion-demo/runs");
    expect(requestInit.method).toBe("POST");
    expect(requestInit.body).toBe(
      JSON.stringify({ idempotency_key: "key-1", scenario: "default" }),
    );
    expect((requestInit.headers as Record<string, string>).Authorization).toBe("Bearer token-1");
  });

  it("URL-encodes organization and run identifiers", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ id: "r", status: "completed" }));
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    await client.getBeaconRun("a/b", "c d", "token");

    const [url] = fetchMock.mock.calls[0] as [string];
    expect(url).toBe("http://localhost:8000/beacon/organizations/a%2Fb/runs/c%20d");
  });

  it("posts an approval decision to the approval endpoint", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ id: "run-1", status: "completed" }));
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    await client.decideBeaconAllocation(
      "zion-demo",
      "run-1",
      { decision: "approve", note: "ok" },
      "token",
    );

    const [url, requestInit] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("http://localhost:8000/beacon/organizations/zion-demo/runs/run-1/approval");
    expect(requestInit.body).toBe(JSON.stringify({ decision: "approve", note: "ok" }));
  });

  it("posts a replay and surfaces typed conflict errors", async () => {
    const fetchMock = vi.fn().mockImplementation(() =>
      Promise.resolve(
        jsonResponse(
          { error: { code: "run_conflict", message: "not dead-lettered", request_id: "req-9" } },
          { status: 409 },
        ),
      ),
    );
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    await expect(client.replayBeaconRun("zion-demo", "run-1", "token")).rejects.toMatchObject({
      status: 409,
      code: "run_conflict",
    });
    await expect(
      client.replayBeaconRun("zion-demo", "run-1", "token"),
    ).rejects.toBeInstanceOf(ZionApiError);
  });

  it("lists runs for one organization", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({ organization_slug: "zion-demo", runs: [] }),
    );
    const client = new ZionApiClient({ baseUrl: "http://localhost:8000", fetch: fetchMock });

    const listing = await client.listBeaconRuns("zion-demo", "token");

    expect(listing.organization_slug).toBe("zion-demo");
    const [url] = fetchMock.mock.calls[0] as [string];
    expect(url).toBe("http://localhost:8000/beacon/organizations/zion-demo/runs");
  });
});
