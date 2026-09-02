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
          title="Shared platform foundation"
          status="implemented"
          summary="A modular FastAPI service with typed errors, request IDs, safe logs,
            strict CORS, and DB-backed health checks, backed by a SQLAlchemy 2 +
            Alembic schema for users, organizations, memberships/roles, expiring
            session tokens, and append-only audit events."
          detailsHref="https://github.com/grey-ghost-1/zion-software-initiative/blob/main/apps/api/README.md"
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
          title="A reusable foundation for public-interest tools"
          status="in-development"
          summary="The goal this foundation exists to serve: giving any future
            public-interest initiative a working, secure base — accounts,
            organizations, roles, and an accessible shell — instead of rebuilding
            one from scratch each time."
          detailsHref="/initiatives"
          detailsLabel="Read the initiatives approach"
        >
          <p className="case-study-card__disclaimer">
            No initiative has launched on this foundation yet, so there is no
            measured field impact, partner, or user to report.
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
          detailsHref="https://github.com/grey-ghost-1/zion-software-initiative/blob/main/apps/web/src/app/page.tsx"
          detailsLabel="Browse apps/web"
        />
      </section>
    </PageShell>
  );
}
