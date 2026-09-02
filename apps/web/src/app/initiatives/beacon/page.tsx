import type { Metadata } from "next";
import { StatusBadge } from "@zion/ui";
import { PageShell } from "@/components/PageShell";

export const metadata: Metadata = {
  title: "Beacon · Zion Software Initiative",
};

const STEPS = [
  { step: "ingest_hazard_fixture", tool: "fixture_loader", outcome: "Succeeded" },
  { step: "validate_geospatial_layer", tool: "geo_validator", outcome: "Succeeded" },
  { step: "record_provenance", tool: "provenance_recorder", outcome: "Succeeded" },
  { step: "evaluate_policy", tool: "policy_evaluator", outcome: "Succeeded" },
  { step: "plan_allocation", tool: "allocation_planner", outcome: "Succeeded" },
  { step: "await_human_approval", tool: "approval_gate", outcome: "Paused for human decision" },
  { step: "record_outcome", tool: "outcome_recorder", outcome: "Succeeded after approval" },
];

const ALLOCATION = [
  {
    zone: "zone-a (severity 5)",
    item: "water_kits",
    qty: 80,
    reason: "priority rank 1: granted min(demand 80, remaining 120)",
  },
  {
    zone: "zone-a (severity 5)",
    item: "meal_packs",
    qty: 120,
    reason: "priority rank 1: granted min(demand 120, remaining 180)",
  },
  {
    zone: "zone-b (severity 4)",
    item: "water_kits",
    qty: 40,
    reason: "priority rank 2: granted min(demand 50, remaining 40)",
  },
  {
    zone: "zone-c (severity 2)",
    item: "water_kits",
    qty: 0,
    reason: "unmet: inventory exhausted after higher-priority zones",
  },
  {
    zone: "zone-d (severity 1)",
    item: "water_kits",
    qty: 0,
    reason: "deferred: below the activation threshold of 2",
  },
];

export default function BeaconPage() {
  return (
    <PageShell active="initiatives">
      <section className="page-hero" aria-labelledby="beacon-title">
        <p className="eyebrow">Initiative demonstration</p>
        <h1 id="beacon-title">Beacon: a deterministic, human-approved readiness workflow</h1>
        <p className="page-intro">
          <StatusBadge status="implemented" label="Working demonstration" /> One synthetic
          coastal-storm scenario runs through a typed, observable workflow: fixture ingestion,
          geospatial and provenance validation, versioned policy checks, an explainable supply
          allocation proposal, and an explicit human approval gate.
        </p>
        <p className="page-intro">
          <strong>Disclosure:</strong> everything on this page and in the Beacon API is a
          synthetic, exploratory demonstration. It uses fabricated fixture data only, is not an
          official hazard product, and issues no warnings. Consult official sources such as the
          National Weather Service for real conditions.
        </p>
      </section>

      <section aria-labelledby="tracks-title">
        <div className="section-heading">
          <p className="eyebrow">Two audiences, one workflow</p>
          <h2 id="tracks-title">Impact and engineering tracks</h2>
        </div>
        <div className="card-grid">
          <article>
            <h3>Impact track</h3>
            <p>
              When a synthetic storm advisory arrives, Beacon validates where the data came from
              and how fresh it is, proposes how limited synthetic supplies could be shared across
              synthetic community zones, explains every line of that proposal, and then stops: a
              human coordinator must approve or reject before anything is recorded as final.
            </p>
          </article>
          <article>
            <h3>Engineering track</h3>
            <p>
              A fixed state machine with typed, allowlisted tools; idempotent run creation;
              bounded retries with explicit timeout and dead-letter states plus safe replay;
              versioned policy evaluation with prompt-injection and sensitive-data guards;
              CRS, geometry, and freshness validation; append-only step events and audit records.
            </p>
          </article>
        </div>
      </section>

      <section aria-labelledby="pipeline-title">
        <div className="section-heading">
          <p className="eyebrow">Recorded deterministic run</p>
          <h2 id="pipeline-title">The pipeline, as list and table</h2>
        </div>
        <p>
          This is the output shape of one recorded run of the demonstration engine (scenario
          &quot;default&quot;, policy version beacon-policy-v1, fixture beacon-coastal-storm-v1).
          Every status below is conveyed in text, not color.
        </p>
        <ol>
          {STEPS.map((row) => (
            <li key={row.step}>
              <strong>{row.step}</strong> via {row.tool} — {row.outcome}
            </li>
          ))}
        </ol>
        <table>
          <caption>Typed workflow steps and outcomes (tabular equivalent)</caption>
          <thead>
            <tr>
              <th scope="col">Step</th>
              <th scope="col">Typed tool</th>
              <th scope="col">Outcome</th>
            </tr>
          </thead>
          <tbody>
            {STEPS.map((row) => (
              <tr key={row.step}>
                <th scope="row">{row.step}</th>
                <td>{row.tool}</td>
                <td>{row.outcome}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section aria-labelledby="allocation-title">
        <div className="section-heading">
          <p className="eyebrow">Explainable heuristic, not an optimizer</p>
          <h2 id="allocation-title">Sample allocation proposal with reasons</h2>
        </div>
        <p>
          A greedy severity/population priority heuristic (no optimality guarantee) allocates
          synthetic inventory with two hard invariants: totals never exceed inventory, and no
          quantity is ever negative. Unmet and deferred demand is reported, never hidden.
        </p>
        <table>
          <caption>Excerpt of one recorded allocation proposal</caption>
          <thead>
            <tr>
              <th scope="col">Zone</th>
              <th scope="col">Item</th>
              <th scope="col">Quantity</th>
              <th scope="col">Reason</th>
            </tr>
          </thead>
          <tbody>
            {ALLOCATION.map((row) => (
              <tr key={`${row.zone}-${row.item}-${row.reason}`}>
                <th scope="row">{row.zone}</th>
                <td>{row.item}</td>
                <td>{row.qty}</td>
                <td>{row.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section aria-labelledby="failure-title">
        <div className="section-heading">
          <p className="eyebrow">Failure is part of the demonstration</p>
          <h2 id="failure-title">Timeouts, dead letters, and safe replay</h2>
        </div>
        <p>
          The &quot;transient-timeout&quot; scenario makes fixture ingestion time out on every
          attempt: the engine records three bounded, timed-out attempts, moves the run to an
          explicit dead-letter state, and a coordinator can later replay that same run — not a
          duplicate — to completion. Malformed CRS, impossible coordinates, stale timestamps, and
          injection-like fixture text each have their own scenario, and each is rejected or
          disclosed with machine-readable codes.
        </p>
      </section>

      <section className="status-section" aria-labelledby="try-title">
        <h2 id="try-title">Inspect it yourself</h2>
        <p>
          The full workflow is exposed by the local demo API: <code>GET /beacon/capabilities</code>{" "}
          lists the fixed workflow, typed tools, scenarios, and guardrails;{" "}
          <code>POST /beacon/organizations/&#123;org&#125;/runs</code> starts an idempotent run;
          approval and replay endpoints require the coordinator or admin role. Every claim is
          verified by the repository&apos;s test suite — see the <a href="/evidence">Evidence</a>{" "}
          page.
        </p>
      </section>
    </PageShell>
  );
}
