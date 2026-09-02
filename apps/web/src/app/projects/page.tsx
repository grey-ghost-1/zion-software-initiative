import type { Metadata } from "next";
import { CaseStudyCard } from "@zion/ui";
import { PageShell } from "@/components/PageShell";

export const metadata: Metadata = {
  title: "Projects · Zion Software Initiative",
};

export default function ProjectsPage() {
  return (
    <PageShell active="projects">
      <section className="page-hero" aria-labelledby="projects-title">
        <p className="eyebrow">Engineering portfolio</p>
        <h1 id="projects-title">What has actually been built</h1>
        <p className="page-intro">
          Each entry below is a real, inspectable piece of this repository — not a
          plan. Every claim links to the code and tests that back it up on the{" "}
          <a href="/evidence">Evidence</a> page.
        </p>
      </section>

      <section className="case-study-grid" aria-label="Case studies">
        <CaseStudyCard
          variant="engineering"
          title="Harbor synthetic coordination workflow"
          status="implemented"
          summary="One end-to-end FastAPI and Next.js demonstration covering bounded
            requests, explainable resource matching, human triage, transactional
            capacity reservation, volunteer plan approval, fulfillment, audit, and
            synthetic metrics."
          detailsHref="/harbor"
          detailsLabel="Open the Harbor case study"
        >
          <ul className="case-study-card__list">
            <li>Deterministic scores expose every component, rejection, and uncertainty</li>
            <li>Unknown or stale capacity cannot be matched or reserved</li>
            <li>Role and organization boundaries are enforced by the API</li>
            <li>No real people, sites, dispatch, maps, notifications, or model calls</li>
          </ul>
        </CaseStudyCard>

        <CaseStudyCard
          variant="engineering"
          title="Shared platform foundation"
          status="implemented"
          summary="A modular FastAPI service with typed errors, request IDs, safe logs,
            strict CORS, and DB-backed health checks, backed by a SQLAlchemy 2 +
            Alembic schema for users, organizations, memberships/roles, expiring
            session tokens, and append-only audit events."
          detailsHref="https://github.com/grey-ghost-1/zion-software-initiative/tree/main/apps/api"
          detailsLabel="Browse apps/api"
        >
          <ul className="case-study-card__list">
            <li>Secure password hashing, login, and a `/me` profile endpoint</li>
            <li>Server-side RBAC and organization isolation (no enumeration)</li>
            <li>One admin-only demonstration endpoint, audited on every use</li>
            <li>41 automated backend tests covering auth, RBAC, and audits</li>
          </ul>
        </CaseStudyCard>

        <CaseStudyCard
          variant="impact"
          title="Harbor's intended public-interest use"
          status="implemented"
          summary="A synthetic exploration of how coordinators could review requests,
            capacity, and volunteer proposals in one transparent workflow while
            retaining human authority."
          detailsHref="/harbor"
          detailsLabel="Read Harbor's impact and safety track"
        >
          <p className="case-study-card__disclaimer">
            This demonstrates software behavior only. There is no deployed service,
            aid provision, real user, partner, or measured field impact.
          </p>
        </CaseStudyCard>

        <CaseStudyCard
          variant="engineering"
          title="Accessible dual-audience web shell"
          status="implemented"
          summary="A Next.js App Router shell with semantic landmarks, a skip link,
            keyboard-visible focus states, and a shared beach-palette design token
            set, serving both a public-interest reader and a recruiter reviewing
            engineering work."
          detailsHref="https://github.com/grey-ghost-1/zion-software-initiative/tree/main/apps/web"
          detailsLabel="Browse apps/web"
        />
      </section>
    </PageShell>
  );
}
