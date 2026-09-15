"use client";

import { useMemo, useState, type FormEvent } from "react";
import {
  ZionApiClient,
  type HarborAuditTimeline,
  type HarborMatchResponse,
  type HarborMetrics,
  type HarborNeed,
  type HarborPlan,
  type HarborVolunteerAvailability,
} from "@zion/api-client";

const ORGANIZATION = "zion-demo";
const DEMO_COORDINATOR = "coordinator@zion.example";
const DEMO_PASSWORD = "ZionDemo!2026";

export type HarborWorkflowClient = Pick<
  ZionApiClient,
  | "login"
  | "createHarborNeed"
  | "getHarborMatches"
  | "triageHarborNeed"
  | "proposeHarborPlan"
  | "listHarborVolunteerAvailability"
  | "approveHarborPlan"
  | "fulfillHarborPlan"
  | "getHarborAudit"
  | "getHarborMetrics"
>;

interface HarborWorkflowProps {
  client?: HarborWorkflowClient;
}

type Phase = "idle" | "loading" | "matches" | "proposed" | "approved" | "fulfilled";

function messageFrom(error: unknown): string {
  return error instanceof Error
    ? error.message
    : "The synthetic workflow could not continue. Review the API and try again.";
}

export function HarborWorkflow({ client: suppliedClient }: HarborWorkflowProps) {
  const defaultClient = useMemo(
    () =>
      new ZionApiClient({
        baseUrl: process.env.NEXT_PUBLIC_ZION_API_URL ?? "http://localhost:8000",
        fetch: globalThis.fetch.bind(globalThis),
      }),
    [],
  );
  const client = suppliedClient ?? defaultClient;
  const [phase, setPhase] = useState<Phase>("idle");
  const [token, setToken] = useState("");
  const [need, setNeed] = useState<HarborNeed | null>(null);
  const [matches, setMatches] = useState<HarborMatchResponse | null>(null);
  const [selectedResource, setSelectedResource] = useState("");
  const [volunteers, setVolunteers] = useState<HarborVolunteerAvailability[]>([]);
  const [selectedVolunteer, setSelectedVolunteer] = useState("");
  const [plan, setPlan] = useState<HarborPlan | null>(null);
  const [audit, setAudit] = useState<HarborAuditTimeline | null>(null);
  const [metrics, setMetrics] = useState<HarborMetrics | null>(null);
  const [error, setError] = useState("");

  async function refreshEvidence(accessToken: string, needId: string) {
    try {
      const [timeline, summary] = await Promise.all([
        client.getHarborAudit(ORGANIZATION, needId, accessToken),
        client.getHarborMetrics(ORGANIZATION, accessToken),
      ]);
      setAudit(timeline);
      setMetrics(summary);
    } catch {
      setError(
        "The workflow step succeeded, but audit or metrics refresh failed. Reload evidence before acting again.",
      );
    }
  }

  async function start(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setPhase("loading");
    setSelectedResource("");
    setSelectedVolunteer("");
    setPlan(null);
    setAudit(null);
    const form = new FormData(event.currentTarget);
    try {
      const session = await client.login({
        email: DEMO_COORDINATOR,
        password: DEMO_PASSWORD,
      });
      const created = await client.createHarborNeed(
        ORGANIZATION,
        {
          request_ref: String(form.get("request_ref")),
          category: String(form.get("category")) as "food" | "temporary_shelter",
          zone: String(form.get("zone")) as "north" | "central" | "south",
          quantity: Number(form.get("quantity")),
          eligibility: String(form.get("eligibility")) as
            | "open_access"
            | "coordinator_referral",
          accessibility_requirement: String(form.get("accessibility_requirement")) as
            | "none"
            | "step_free",
          urgency: String(form.get("urgency")) as "standard" | "time_sensitive",
        },
        session.access_token,
      );
      const [explained, availability] = await Promise.all([
        client.getHarborMatches(ORGANIZATION, created.id, session.access_token),
        client.listHarborVolunteerAvailability(ORGANIZATION, session.access_token),
      ]);
      setToken(session.access_token);
      setNeed(created);
      setMatches(explained);
      setVolunteers(availability.items);
      setPhase("matches");
      await refreshEvidence(session.access_token, created.id);
    } catch (workflowError) {
      setError(messageFrom(workflowError));
      setPhase("idle");
    }
  }

  async function propose() {
    if (!need || !selectedResource || !selectedVolunteer || !token) return;
    setError("");
    setPhase("loading");
    try {
      await client.triageHarborNeed(
        ORGANIZATION,
        need.id,
        {
          decision: "ready",
          reason: "match_explanation_reviewed",
          selected_resource_id: selectedResource,
        },
        token,
      );
      const proposed = await client.proposeHarborPlan(
        ORGANIZATION,
        need.id,
        {
          resource_id: selectedResource,
          volunteer_availability_id: selectedVolunteer,
        },
        token,
      );
      setPlan(proposed);
      setPhase("proposed");
      await refreshEvidence(token, need.id);
    } catch (workflowError) {
      setError(messageFrom(workflowError));
      setPhase("matches");
    }
  }

  async function approve() {
    if (!need || !plan || !token) return;
    setError("");
    setPhase("loading");
    try {
      const approved = await client.approveHarborPlan(ORGANIZATION, plan.id, token);
      setPlan(approved);
      setPhase("approved");
      await refreshEvidence(token, need.id);
    } catch (workflowError) {
      setError(messageFrom(workflowError));
      setPhase("proposed");
    }
  }

  async function fulfill() {
    if (!need || !plan || !token) return;
    setError("");
    setPhase("loading");
    try {
      const fulfilled = await client.fulfillHarborPlan(ORGANIZATION, plan.id, token);
      setPlan(fulfilled);
      setPhase("fulfilled");
      await refreshEvidence(token, need.id);
    } catch (workflowError) {
      setError(messageFrom(workflowError));
      setPhase("approved");
    }
  }

  const isLoading = phase === "loading";

  return (
    <section className="harbor-workflow" aria-labelledby="workflow-title" aria-busy={isLoading}>
      <div className="section-heading">
        <p className="eyebrow">Interactive synthetic workflow</p>
        <h2 id="workflow-title">Request to transparent audit</h2>
        <p>
          This local demonstration signs in as the published synthetic coordinator account.
          Every proposal, approval, and fulfillment step waits for your explicit action.
        </p>
      </div>

      <p className="harbor-disclosure">
        <strong>Synthetic data only:</strong> no real person, address, shelter, volunteer,
        capacity, or aid delivery is represented.
      </p>

      <form
        className="harbor-form"
        onSubmit={start}
        aria-label="Synthetic Harbor workflow"
      >
        <label>
          Synthetic request reference
          <input
            name="request_ref"
            defaultValue="DEMO-WEB-701"
            pattern="DEMO-[A-Z0-9-]{3,20}"
            maxLength={25}
            required
          />
        </label>
        <label>
          Need category
          <select name="category" defaultValue="food">
            <option value="food">Food</option>
            <option value="temporary_shelter">Temporary shelter</option>
          </select>
        </label>
        <label>
          Coarse zone
          <select name="zone" defaultValue="central">
            <option value="north">North</option>
            <option value="central">Central</option>
            <option value="south">South</option>
          </select>
        </label>
        <label>
          Units requested
          <input name="quantity" type="number" min={1} max={8} defaultValue={2} required />
        </label>
        <label>
          Controlled eligibility
          <select name="eligibility" defaultValue="open_access">
            <option value="open_access">Open access</option>
            <option value="coordinator_referral">Coordinator referral</option>
          </select>
        </label>
        <label>
          Accessibility requirement
          <select name="accessibility_requirement" defaultValue="none">
            <option value="none">No step-free requirement specified</option>
            <option value="step_free">Step-free</option>
          </select>
        </label>
        <label>
          Time classification
          <select name="urgency" defaultValue="standard">
            <option value="standard">Standard</option>
            <option value="time_sensitive">Time-sensitive</option>
          </select>
        </label>
        <button type="submit" disabled={isLoading}>
          Create synthetic request and explain matches
        </button>
      </form>

      <div className="harbor-status" role="status" aria-live="polite">
        {isLoading
          ? "Working on the selected synthetic step..."
          : phase === "idle"
            ? "Ready to begin. No request has been created in this session."
            : `Current workflow status: ${phase}.`}
      </div>
      {error ? <p role="alert" className="harbor-error">{error}</p> : null}

      {matches ? (
        <section className="harbor-results" aria-labelledby="match-title">
          <h3 id="match-title">Transparent match options for {matches.need.request_ref}</h3>
          <p>{matches.scoring_notice}</p>
          {matches.matches.length === 0 ? (
            <p className="harbor-empty">No currently safe match is available. Nothing was assigned.</p>
          ) : (
            <fieldset disabled={phase !== "matches"}>
              <legend>Select one explained option; Harbor does not choose for you</legend>
              <div className="harbor-match-grid">
                {matches.matches.map((match) => (
                  <label className="harbor-match" key={match.resource.id}>
                    <span>
                      <input
                        type="radio"
                        name="selected_resource"
                        value={match.resource.id}
                        checked={selectedResource === match.resource.id}
                        onChange={(event) => setSelectedResource(event.target.value)}
                      />
                      <strong>{match.resource.name}</strong> — score {match.score}
                    </span>
                    <span>{match.resource.zone} zone · {match.resource.accessibility}</span>
                    <details>
                      <summary>Why this option scored this way</summary>
                      <ul>
                        {match.score_components.map((component) => (
                          <li key={component.rule}>
                            {component.explanation} (+{component.points})
                          </li>
                        ))}
                      </ul>
                      {match.uncertainty.map((note) => <p key={note}>{note}</p>)}
                    </details>
                  </label>
                ))}
              </div>
            </fieldset>
          )}
          {phase === "matches" && matches.matches.length > 0 ? (
            <>
              <fieldset className="harbor-volunteers">
                <legend>Select synthetic volunteer availability</legend>
                {volunteers
                  .filter(
                    (volunteer) =>
                      volunteer.available && volunteer.category === matches.need.category,
                  )
                  .map((volunteer) => (
                    <label key={volunteer.id}>
                      <input
                        type="radio"
                        name="selected_volunteer"
                        value={volunteer.id}
                        checked={selectedVolunteer === volunteer.id}
                        onChange={(event) => setSelectedVolunteer(event.target.value)}
                      />
                      {volunteer.code} — {volunteer.zone} zone
                    </label>
                  ))}
              </fieldset>
              <button
                type="button"
                onClick={propose}
                disabled={!selectedResource || !selectedVolunteer}
              >
                Record triage and propose volunteer plan
              </button>
            </>
          ) : null}
          <details className="harbor-rejections">
            <summary>Review rejected resources ({matches.rejected.length})</summary>
            <ul>
              {matches.rejected.map((item) => (
                <li key={item.resource.id}>
                  <strong>{item.resource.name}</strong>: {item.rejected_reasons.join(", ")}
                </li>
              ))}
            </ul>
          </details>
        </section>
      ) : null}

      {plan ? (
        <section className="harbor-plan" aria-labelledby="plan-title">
          <h3 id="plan-title">Coordinator-reviewed plan</h3>
          <dl>
            <div><dt>Resource</dt><dd>{plan.resource_name}</dd></div>
            <div><dt>Volunteer availability</dt><dd>{plan.volunteer_code}</dd></div>
            <div><dt>Units</dt><dd>{plan.quantity}</dd></div>
            <div><dt>Status</dt><dd>{plan.status}</dd></div>
          </dl>
          {phase === "proposed" ? (
            <button type="button" onClick={approve}>
              Explicitly approve and reserve capacity
            </button>
          ) : null}
          {phase === "approved" ? (
            <button type="button" onClick={fulfill}>
              Record synthetic fulfillment
            </button>
          ) : null}
        </section>
      ) : null}

      {audit && audit.items.length > 0 ? (
        <section className="harbor-audit" aria-labelledby="audit-title">
          <h3 id="audit-title">Append-only audit timeline</h3>
          <ol>
            {audit.items.map((item) => (
              <li key={item.id}>
                <strong>{item.action.replaceAll("_", " ")}</strong>
              </li>
            ))}
          </ol>
        </section>
      ) : null}

      {metrics ? (
        <section className="harbor-metrics" aria-labelledby="metrics-title">
          <h3 id="metrics-title">Small synthetic metrics summary</h3>
          <dl>
            <div><dt>Requests</dt><dd>{metrics.total_requests}</dd></div>
            <div><dt>Awaiting approval</dt><dd>{metrics.awaiting_approval}</dd></div>
            <div><dt>Fulfilled requests</dt><dd>{metrics.fulfilled_requests}</dd></div>
            <div><dt>Available resources</dt><dd>{metrics.currently_available_resources}</dd></div>
          </dl>
        </section>
      ) : null}
    </section>
  );
}
