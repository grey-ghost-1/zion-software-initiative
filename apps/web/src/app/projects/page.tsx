import type { Metadata } from "next";
import { CaseStudyCard } from "@zion/ui";
import { PageShell } from "@/components/PageShell";

export const metadata: Metadata = {
  title: "Projects · Zion Software Initiative",
};

export default function ProjectsPage() {
  return (
    <PageShell active="flagships">
      <section className="page-hero" aria-labelledby="projects-title">
        <p className="eyebrow">Zion project areas</p>
        <h1 id="projects-title">Two first-class project pages, one shared foundation</h1>
        <p className="page-intro">
          These project pages are the front door for the Zion work. Each one now has a
          truthful page for purpose, audience, features, limitations, and evidence — not
          just a summary card.
        </p>
        <nav className="project-nav" aria-label="Project pages">
          <a href="/projects/community-aid-hub">Community Aid Hub</a>
          <a href="/projects/health-navigator">Health Navigator</a>
          <a href="/initiatives">Initiatives</a>
        </nav>
      </section>

      <section className="project-index" aria-labelledby="project-pages-title">
        <div className="section-heading">
          <p className="eyebrow">Project index</p>
          <h2 id="project-pages-title">The two Zion project routes</h2>
          <p>
            The index keeps the cloud theme calm and readable while the navy accents make
            the structure feel anchored instead of decorative.
          </p>
        </div>
        <div className="case-study-grid">
          <CaseStudyCard
            variant="impact"
            title="Community Aid Hub"
            status="implemented"
            summary="A synthetic coordination workspace for aid requests, matching, triage, fulfillment, and audit trails."
            detailsHref="/projects/community-aid-hub"
            detailsLabel="Open Community Aid Hub"
          >
            <ul className="case-study-card__list">
              <li>Purpose: keep aid coordination legible and calm.</li>
              <li>Audience: coordinators, volunteers, and engineers.</li>
              <li>Evidence: Harbor route, API, UI, and tests.</li>
            </ul>
          </CaseStudyCard>

          <CaseStudyCard
            variant="impact"
            title="Health Navigator"
            status="implemented"
            summary="A non-diagnostic health-access navigator with crisis-first routing, explanation cards, and curated references."
            detailsHref="/projects/health-navigator"
            detailsLabel="Open Health Navigator"
          >
            <ul className="case-study-card__list">
              <li>Purpose: make the first step feel clear and safe.</li>
              <li>Audience: visitors, navigators, and engineers.</li>
              <li>Evidence: Haven page, demo, API route, and tests.</li>
            </ul>
          </CaseStudyCard>

        </div>
      </section>

      <section className="project-index" aria-labelledby="foundation-title">
        <div className="section-heading">
          <p className="eyebrow">Supporting work</p>
          <h2 id="foundation-title">Shared foundation and shell</h2>
          <p>
            The project areas sit on a shared platform foundation and an accessible web
            shell, so the route map stays consistent as the site grows.
          </p>
        </div>
        <div className="case-study-grid">
          <CaseStudyCard
            variant="engineering"
            title="Shared platform foundation"
            status="implemented"
            summary="A modular FastAPI service with typed errors, request IDs, safe logs, strict CORS, and DB-backed health checks."
            detailsHref="https://github.com/grey-ghost-1/zion-software-initiative/blob/main/apps/api/README.md"
            detailsLabel="Browse apps/api"
          >
            <ul className="case-study-card__list">
              <li>Secure password hashing, login, and a /me endpoint</li>
              <li>Server-side RBAC and organization isolation</li>
              <li>Append-only audit events and backend tests</li>
            </ul>
          </CaseStudyCard>

          <CaseStudyCard
            variant="engineering"
            title="Accessible dual-audience web shell"
            status="implemented"
            summary="A Next.js App Router shell with semantic landmarks, a skip link, focus states, and shared beach-palette design tokens."
            detailsHref="https://github.com/grey-ghost-1/zion-software-initiative/blob/main/apps/web/src/app/page.tsx"
            detailsLabel="Browse apps/web"
          />
        </div>
      </section>
    </PageShell>
  );
}
