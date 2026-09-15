import type { Metadata } from "next";
import { StatusBadge } from "@zion/ui";
import { PageShell } from "@/components/PageShell";
import { HarborWorkflow } from "./HarborWorkflow";

export const metadata: Metadata = {
  title: "Community Aid Hub · Zion Software Initiative",
  description: "A synthetic, explainable care coordination demonstration for the vulnerable.",
};

export default function HarborPage() {
  return (
    <PageShell active="flagships">
      <section className="page-hero harbor-hero" aria-labelledby="harbor-title">
        <p className="eyebrow">Harbor vertical slice</p>
        <h1 id="harbor-title">Community Aid Hub: care for the vulnerable</h1>
        <p className="page-intro">
          Community Aid Hub is a bounded synthetic prototype for reviewing assistance
          requests, resource capacity, volunteer plans, and an audit trail without
          collecting real vulnerable-person data or making autonomous decisions.
        </p>
        <p><StatusBadge status="implemented" label="Synthetic prototype implemented" /></p>
      </section>

      <section className="harbor-dual-track" aria-label="Harbor case study">
        <article className="case-study-card case-study-card--impact">
          <p className="case-study-card__eyebrow">Impact information</p>
          <h2>What this prototype is intended to explore</h2>
          <p>
            Community coordinators need one understandable view of requests, resource
            fit, shelter-like capacity, volunteer availability, and delivery progress.
            The intended stakeholders are community coordinators, volunteers, service
            organizations, and people evaluating safer coordination practices.
          </p>
          <h3>Dignity, privacy, and safety</h3>
          <p>
            The demo uses controlled categories, coarse fictional zones, synthetic
            codes, and bounded quantities. It excludes names, contacts, precise
            addresses, confidential sites, medical or disability details, immigration
            or benefit data, minors, and unrestricted narrative text. Protected traits
            are absent from matching.
          </p>
          <h3>Prototype status and limitations</h3>
          <p>
            This is an inspectable software demonstration, not an emergency, dispatch,
            case-management, shelter-booking, or aid-delivery service. It has no real
            users, partners, current capacity feed, map, notification system, field
            impact, or deployment.
          </p>
        </article>

        <article className="case-study-card case-study-card--engineering">
          <p className="case-study-card__eyebrow">Engineering evidence</p>
          <h2>Controls visible in the workflow</h2>
          <ul>
            <li>Organization-scoped SQLAlchemy records and server-side role checks</li>
            <li>Deterministic rules with score components, rejection codes, and uncertainty</li>
            <li>Unknown or stale capacity is never presented as available</li>
            <li>Atomic conditional reservation plus a database no-overbooking constraint</li>
            <li>Coordinator triage, proposal, explicit approval, fulfillment, and immutable audit events</li>
            <li>A typed client shared by the route and API contract tests</li>
          </ul>
          <h3>Roadmap, not current capability</h3>
          <p>
            Partner review would be required before any real-world design. Possible
            future research includes carefully governed OpenFEMA data, maps, geocoding,
            notifications, or dispatch. Those are deliberately absent. See the{" "}
            <a href="https://www.fema.gov/about/openfema/terms-conditions">
              OpenFEMA terms
            </a>,{" "}
            <a href="https://centre.humdata.org/data-responsibility/">
              OCHA Data Responsibility guidance
            </a>, and{" "}
            <a href="https://www.w3.org/WAI/standards-guidelines/wcag/">WCAG 2.2</a>.
          </p>
        </article>
      </section>

      <HarborWorkflow />
    </PageShell>
  );
}
