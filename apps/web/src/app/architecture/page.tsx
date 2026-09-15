import type { Metadata } from "next";
import { StatusBadge } from "@zion/ui";
import { PageShell } from "@/components/PageShell";
import { ArchitectureDiagram } from "./ArchitectureDiagram";

export const metadata: Metadata = {
  title: "Architecture · Zion Software Initiative",
  description: "The truthful architecture and production-readiness status of Zion.",
};

const principles = [
  "Synthetic data only",
  "Deterministic safety rules",
  "Transparent decisions",
  "Provenance",
  "RBAC and organization isolation",
  "Audit trails",
  "No diagnosis or treatment",
  "No autonomous dispatch",
  "No real PHI",
  "Human approval for sensitive actions",
] as const;

export default function ArchitecturePage() {
  return (
    <PageShell active="projects">
      <section className="page-hero" aria-labelledby="architecture-title">
        <p className="eyebrow">Platform architecture</p>
        <h1 id="architecture-title">One bounded foundation, two domain modules</h1>
        <p className="page-intro">
          Zion is a typed web and API platform organized as a modular monolith. Harbor
          demonstrates community coordination; Haven demonstrates non-diagnostic
          navigation. Shared controls make their decisions reviewable without suggesting
          that either module is operational.
        </p>
      </section>

      <section aria-labelledby="diagram-title">
        <div className="section-heading">
          <p className="eyebrow">System view</p>
          <h2 id="diagram-title">Request flow and shared foundation</h2>
        </div>
        <ArchitectureDiagram />
        <div className="table-wrapper">
          <table>
            <caption>Semantic text equivalent of the platform diagram</caption>
            <thead>
              <tr>
                <th scope="col">Layer</th>
                <th scope="col">Responsibility</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <th scope="row">Next.js UI</th>
                <td>Accessible public pages and synthetic, human-in-the-loop workflows.</td>
              </tr>
              <tr>
                <th scope="row">Typed API client</th>
                <td>Shared request and response contracts between the UI and API.</td>
              </tr>
              <tr>
                <th scope="row">FastAPI modular monolith</th>
                <td>Harbor and Haven routes, domain services, validation, and authorization.</td>
              </tr>
              <tr>
                <th scope="row">PostgreSQL</th>
                <td>Organization-scoped synthetic records, constraints, and audit history.</td>
              </tr>
              <tr>
                <th scope="row">Cross-cutting layers</th>
                <td>Authentication, RBAC, organization isolation, audit, safety, and provenance.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section aria-labelledby="principles-title">
        <div className="section-heading">
          <p className="eyebrow">Shared principles</p>
          <h2 id="principles-title">Controls that travel with every workflow</h2>
        </div>
        <ul className="evidence-list">
          {principles.map((principle) => (
            <li className="evidence-item" key={principle}>
              {principle}
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="together-title">
        <div className="section-heading">
          <p className="eyebrow">Why these modules exist together</p>
          <h2 id="together-title">Different domains expose the same engineering obligations</h2>
        </div>
        <p>
          Community resource coordination and health-access navigation both involve
          incomplete information, power differences, and potentially consequential next
          steps. Building them on one foundation tests whether transparent rules,
          organization boundaries, provenance, audits, and human approval can remain
          consistent while domain logic stays separate.
        </p>
      </section>

      <section aria-labelledby="readiness-title">
        <div className="section-heading">
          <p className="eyebrow">Production readiness</p>
          <h2 id="readiness-title">Implemented checks are not a production claim</h2>
        </div>
        <div className="card-grid">
          <article>
            <h3>Implemented and repository-verified</h3>
            <p>
              <StatusBadge status="implemented" label="Implemented" /> Automated CI runs
              lint, type, test, and build checks. FastAPI health and readiness endpoints
              are implemented and exercised by repository tests.
            </p>
          </article>
          <article>
            <h3>Pending production verification</h3>
            <p>
              <StatusBadge status="planned" label="Not production-verified" /> Deployment,
              managed PostgreSQL, HTTPS termination, operational monitoring, and rollback
              verification remain pending. No production environment or service-level
              claim is presented.
            </p>
          </article>
        </div>
      </section>

      <section className="boundaries" aria-labelledby="evidence-title">
        <h2 id="evidence-title">Recruiter evidence</h2>
        <p>
          Reviewers can inspect the <a href="/flagships">module catalog</a>,{" "}
          <a href="/evidence">evidence inventory</a>, and repository source for the typed
          client, FastAPI routes, deterministic services, migrations, and tests. The
          architecture is presented as implemented software plus explicit operational gaps,
          not as a deployed case study.
        </p>
      </section>
    </PageShell>
  );
}
