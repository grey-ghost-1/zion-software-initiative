import type { Metadata } from "next";
import { StatusBadge } from "@zion/ui";
import { PageShell } from "@/components/PageShell";
import { beaconConcept, interoperabilityConcepts } from "@/content/concepts";
import { flagshipModules } from "@/content/flagships";
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
    <PageShell active="architecture">
      <section className="page-hero" aria-labelledby="architecture-title">
        <p className="eyebrow">Platform architecture</p>
        <h1 id="architecture-title">One governed platform, two implemented modules</h1>
        <p className="page-intro">
          Zion is a typed web and API platform organized as a modular monolith. Harbor
          demonstrates community coordination; Haven demonstrates non-diagnostic
          navigation. Shared controls make their decisions reviewable without suggesting
          that either module is operational.
        </p>
        <p>
          Beacon is a roadmap-only governance/workflow concept. Zion Labs separates
          concept-only interoperability from attributed prior audited work. Static
          concept pages are not additional implemented modules.
        </p>
      </section>

      <section aria-labelledby="module-status-title">
        <h2 id="module-status-title">Platform catalog and implementation status</h2>
        <div className="card-grid">
          {flagshipModules.map((module) => (
            <article key={module.id}>
              <h3><a href={module.route}>{module.name}</a></h3>
              <p><StatusBadge status="implemented" label={module.status.label} /></p>
              <p>{module.fit}</p>
              <p>{module.status.operationalLabel}</p>
            </article>
          ))}
          <article>
            <h3><a href={beaconConcept.route}>Beacon governance/workflow concept</a></h3>
            <p><StatusBadge status="planned" label="Concept / roadmap" /></p>
            <p>
              Unimplemented, non-operational, synthetic-only. A static web scaffold,
              not a restored runtime or a third implemented flagship.
            </p>
          </article>
          <article>
            <h3><a href="/labs">Zion Labs</a></h3>
            <p><StatusBadge status="planned" label="Concept / roadmap" /> Interoperability only.</p>
            <p>Unimplemented, non-operational, synthetic-only learning concepts:</p>
            <ul>
              {interoperabilityConcepts.map((concept) => (
                <li key={concept.id}><a href={concept.route}>{concept.name}</a></li>
              ))}
            </ul>
            <p>
              <a href="/labs/prior-work">Prior Audited Work</a> is a separate, attributed
              external evidence index, not Zion implementation evidence.
            </p>
          </article>
        </div>
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
        <p>
          These controls describe the implemented Harbor/Haven foundation. For Beacon
          and interoperability concepts they are design requirements, not implemented
          protections or evidence of standards conformance or HIPAA compliance.
        </p>
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
              hosted deployment, managed production PostgreSQL, public HTTPS verification,
              operational monitoring, and a rollback exercise remain pending or unverified.
              No production environment or service-level
              claim is presented.
            </p>
          </article>
        </div>
        <div className="card-grid">
          <article>
            <h3>CI/CD</h3>
            <p>
              <StatusBadge status="planned" label="Production evidence placeholder" />{" "}
              CI checks exist; continuous deployment is not production-verified.
              Add release approval and deployment evidence only after validation.
            </p>
          </article>
          <article>
            <h3>Health</h3>
            <p>
              <StatusBadge status="planned" label="Production evidence placeholder" />{" "}
              Repository-tested health/readiness endpoints are not hosted availability
              evidence. Add production probe and alert verification only after validation.
            </p>
          </article>
          <article>
            <h3>Logging</h3>
            <p>
              <StatusBadge status="planned" label="Production evidence placeholder" />{" "}
              Audit records are not proof of operational log collection or alerting.
              Production log handling, redaction, retention, and access verification remain
              unverified; add evidence only after validation.
            </p>
          </article>
          <article>
            <h3>Rollback</h3>
            <p>
              <StatusBadge status="planned" label="Production evidence placeholder" />{" "}
              No production rollback exercise is verified. Add a validated recovery
              procedure and exercise evidence only after implementation and validation.
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
