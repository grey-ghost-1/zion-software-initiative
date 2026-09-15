import type { Metadata } from "next";
import { StatusBadge } from "@zion/ui";
import { PageShell } from "@/components/PageShell";

export const metadata: Metadata = {
  title: "Mission · Zion Software Initiative",
  description:
    "Zion's responsible-engineering mission across community coordination and non-diagnostic navigation.",
};

export default function MissionPage() {
  return (
    <PageShell active="home">
      <section className="page-hero" aria-labelledby="mission-title">
        <p className="eyebrow">One responsible-engineering platform</p>
        <h1 id="mission-title">Human judgment stays at the center of consequential workflows</h1>
        <p className="page-intro">
          Zion explores how software can support safer community coordination and
          non-diagnostic navigation without replacing the people responsible for the
          decision. It is one platform with two shipping modules: Harbor and Haven.
        </p>
        <p>
          <StatusBadge status="implemented" label="Synthetic demonstrations implemented" />{" "}
          <strong>Non-operational:</strong> Zion is not deployed, production-verified, or
          used by real communities, patients, partners, or service organizations.
        </p>
      </section>

      <section aria-labelledby="public-title">
        <div className="section-heading">
          <p className="eyebrow">For the public</p>
          <h2 id="public-title">What responsible support should feel like</h2>
        </div>
        <div className="card-grid">
          <article>
            <h3>Clear, not opaque</h3>
            <p>
              People should be able to understand why a workflow suggests a next step,
              what information it used, and where its authority ends.
            </p>
          </article>
          <article>
            <h3>Assistive, not autonomous</h3>
            <p>
              Sensitive actions require human review and approval. Zion does not dispatch
              resources, diagnose, prescribe, treat, or contact services on anyone&apos;s behalf.
            </p>
          </article>
          <article>
            <h3>Bounded by design</h3>
            <p>
              Published demonstrations use synthetic data and deterministic safety rules,
              with explicit limitations instead of claims about real-world outcomes.
            </p>
          </article>
        </div>
      </section>

      <section aria-labelledby="recruiter-title">
        <div className="section-heading">
          <p className="eyebrow">For recruiters and engineering reviewers</p>
          <h2 id="recruiter-title">The portfolio thesis</h2>
        </div>
        <p>
          Zion demonstrates a typed Next.js-to-FastAPI platform, modular domain boundaries,
          PostgreSQL persistence, organization-scoped RBAC, deterministic safety behavior,
          provenance, and auditable human approval. The goal is not to present a fictional
          startup; it is to make engineering judgment inspectable.
        </p>
        <nav className="project-index-nav" aria-label="Mission evidence">
          <a href="/flagships">Review the two flagship modules</a>
          <a href="/architecture">Inspect the platform architecture</a>
          <a href="/evidence">Trace implemented claims to repository evidence</a>
        </nav>
      </section>

      <section className="boundaries" aria-labelledby="mission-boundaries-title">
        <h2 id="mission-boundaries-title">Current boundary</h2>
        <p>
          Zion has no production deployment, real PHI, live service integrations, field
          users, partner commitments, or measured impact. Harbor is not an emergency or
          autonomous dispatch service. Haven is not a medical service and provides no
          diagnosis, treatment, or medical advice.
        </p>
      </section>
    </PageShell>
  );
}
