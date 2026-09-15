import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type {
  HarborAuditTimeline,
  HarborMatchResponse,
  HarborMetrics,
  HarborNeed,
  HarborPlan,
} from "@zion/api-client";
import { HarborWorkflow, type HarborWorkflowClient } from "./HarborWorkflow";
import HarborPage from "./page";

const need: HarborNeed = {
  id: "need-1",
  request_ref: "DEMO-WEB-701",
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
};

const resourceName = '<img src=x onerror="alert(1)"> Synthetic pantry';
const matches: HarborMatchResponse = {
  need,
  matches: [
    {
      resource: {
        id: "resource-1",
        code: "RES-1",
        name: resourceName,
        category: "food",
        zone: "central",
        eligibility: "open_access",
        accessibility: "step_free",
        status: "open",
        capacity: {
          total_units: 4,
          reserved_units: 0,
          fulfilled_units: 0,
          available_units: 4,
          freshness: "current",
        },
        synthetic: true,
      },
      score: 100,
      score_components: [
        { rule: "need_category", points: 30, explanation: "Category matches." },
      ],
      rejected_reasons: [],
      uncertainty: ["Coarse zones only."],
    },
  ],
  rejected: [],
  scoring_notice: "A coordinator makes every decision.",
  protected_traits_used: false,
};

const proposedPlan: HarborPlan = {
  id: "plan-1",
  need_id: need.id,
  request_ref: need.request_ref,
  resource_id: "resource-1",
  resource_name: resourceName,
  resource_zone: "central",
  category: "food",
  quantity: 2,
  volunteer_code: "VOL-CENTRAL-FOOD",
  status: "proposed",
  proposed_at: "2026-09-01T00:01:00Z",
  approved_at: null,
  fulfilled_at: null,
  synthetic: true,
};

const audit: HarborAuditTimeline = {
  need_id: need.id,
  items: [
    {
      id: "audit-1",
      occurred_at: "2026-09-01T00:00:00Z",
      action: "harbor.need_created",
      context: {},
    },
  ],
};

const metrics: HarborMetrics = {
  total_requests: 4,
  submitted_requests: 2,
  active_plans: 1,
  awaiting_approval: 1,
  fulfilled_requests: 0,
  currently_available_resources: 2,
  reserved_units: 4,
  fulfilled_units: 4,
  synthetic_disclosure: "Synthetic demonstration data only.",
};

function fakeClient(): HarborWorkflowClient {
  return {
    login: vi.fn().mockResolvedValue({
      access_token: "token",
      token_type: "bearer",
      expires_at: "2026-09-02T00:00:00Z",
    }),
    createHarborNeed: vi.fn().mockResolvedValue(need),
    getHarborMatches: vi.fn().mockResolvedValue(matches),
    triageHarborNeed: vi.fn().mockResolvedValue({ ...need, status: "triaged" }),
    proposeHarborPlan: vi.fn().mockResolvedValue(proposedPlan),
    listHarborVolunteerAvailability: vi.fn().mockResolvedValue({
      items: [
        {
          id: "volunteer-1",
          code: "VOL-CENTRAL-FOOD",
          zone: "central",
          category: "food",
          available: true,
        },
      ],
      selection_notice: "A coordinator must choose.",
    }),
    approveHarborPlan: vi.fn().mockResolvedValue({
      ...proposedPlan,
      status: "approved",
      approved_at: "2026-09-01T00:02:00Z",
    }),
    fulfillHarborPlan: vi.fn().mockResolvedValue({
      ...proposedPlan,
      status: "fulfilled",
      approved_at: "2026-09-01T00:02:00Z",
      fulfilled_at: "2026-09-01T00:03:00Z",
    }),
    getHarborAudit: vi.fn().mockResolvedValue(audit),
    getHarborMetrics: vi.fn().mockResolvedValue(metrics),
  };
}

describe("Harbor page", () => {
  it("presents both tracks, synthetic boundaries, limitations, and authoritative roadmap links", () => {
    render(<HarborPage />);

    const nav = screen.getByRole("navigation", { name: "Primary" });
    expect(within(nav).getByRole("link", { name: "Flagships" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByText("Impact information")).toBeVisible();
    expect(screen.getByText("Engineering evidence")).toBeVisible();
    expect(screen.getAllByText(/synthetic data only/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/no real users, partners, current capacity feed/i)).toBeVisible();
    expect(screen.getByRole("link", { name: "OpenFEMA terms" })).toHaveAttribute(
      "href",
      "https://www.fema.gov/about/openfema/terms-conditions",
    );
  });

  it("keeps proposal, approval, and fulfillment explicit with semantic live status", async () => {
    const client = fakeClient();
    const { container } = render(<HarborWorkflow client={client} />);

    expect(screen.getByRole("status")).toHaveTextContent("Ready to begin");
    fireEvent.submit(screen.getByRole("button", { name: /create synthetic request/i }).closest("form")!);

    const option = await screen.findByRole("radio", { name: new RegExp("Synthetic pantry") });
    expect(container.querySelector("img")).toBeNull();
    expect(screen.getByText(resourceName, { exact: false })).toBeVisible();
    fireEvent.click(option);
    fireEvent.click(screen.getByRole("radio", { name: /VOL-CENTRAL-FOOD/i }));
    fireEvent.click(screen.getByRole("button", { name: /propose volunteer plan/i }));

    const approve = await screen.findByRole("button", { name: /explicitly approve/i });
    expect(screen.queryByRole("button", { name: /record synthetic fulfillment/i })).toBeNull();
    fireEvent.click(approve);
    const fulfill = await screen.findByRole("button", { name: /record synthetic fulfillment/i });
    fireEvent.click(fulfill);

    await waitFor(() =>
      expect(screen.getByRole("status")).toHaveTextContent("Current workflow status: fulfilled"),
    );
    expect(client.triageHarborNeed).toHaveBeenCalledWith(
      "zion-demo",
      "need-1",
      expect.objectContaining({ decision: "ready", selected_resource_id: "resource-1" }),
      "token",
    );
    expect(client.approveHarborPlan).toHaveBeenCalledBefore(
      client.fulfillHarborPlan as ReturnType<typeof vi.fn>,
    );
  });

  it("announces API failures as an alert and restores an actionable form", async () => {
    const client = fakeClient();
    vi.mocked(client.login).mockRejectedValueOnce(new Error("Synthetic API unavailable"));
    render(<HarborWorkflow client={client} />);

    fireEvent.submit(screen.getByRole("button", { name: /create synthetic request/i }).closest("form")!);

    expect(await screen.findByRole("alert")).toHaveTextContent("Synthetic API unavailable");
    expect(screen.getByRole("button", { name: /create synthetic request/i })).toBeEnabled();
  });
});
