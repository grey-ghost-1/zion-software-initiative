import type { Metadata } from "next";
import { CaseStudyCard, StatusBadge } from "@zion/ui";
import { PageShell } from "@/components/PageShell";
import { HavenDemo } from "./HavenDemo";

export const metadata: Metadata = {
  title: "Health Navigator · Zion Software Initiative",
};

export default function HavenPage() {
  return (
    <PageShell active="initiatives">
      <section className="page-hero" aria-labelledby="haven-title">
        <p className="eyebrow">Initiative demonstration</p>
        <h1 id="haven-title">Health Navigator: healing &amp; health access</h1>
        <p className="page-intro">
          <StatusBadge status="implemented" label="Working demonstration" /> Health
          Navigator is a working demonstration of non-diagnostic health-access
          navigation: synthetic, ephemeral scenarios only — never real patients,
          medical records, or advice.
        </p>
        <p className="page-intro">
          <strong>Haven is not a medical service.</strong> It does not provide diagnosis,
          treatment, or medical advice, and it is not affiliated with any healthcare
          provider. Nothing you type in the demonstration is sent, stored, or monitored.
        </p>
      </section>

      <section aria-label="Emergency help" role="region" className="status-section">
        <h2>If you need help right now</h2>
        <p>
          If anyone is in immediate physical danger, <strong>call 911</strong> (United
          States). If you may hurt yourself or someone else,{" "}
          <strong>call or text 988</strong> or chat at{" "}
          <a href="https://988lifeline.org/">988lifeline.org</a> to reach the 988 Suicide
          &amp; Crisis Lifeline — free, confidential, 24/7. This page does not monitor you
          or contact anyone on your behalf.
        </p>
      </section>

      <section aria-labelledby="haven-demo-title">
        <div className="section-heading">
          <p className="eyebrow">Try it</p>
          <h2 id="haven-demo-title">Synthetic concern → routing → review demonstration</h2>
        </div>
        <HavenDemo />
      </section>

      <section aria-labelledby="haven-tracks-title">
        <div className="section-heading">
          <p className="eyebrow">Two honest tracks</p>
          <h2 id="haven-tracks-title">Impact and engineering</h2>
        </div>
        <div className="case-study-grid">
          <CaseStudyCard
            variant="impact"
            title="Why navigation, not diagnosis"
            status="implemented"
            summary="Many people delay care because instructions are confusing, costs are unclear, or they do not know where to start. Health Navigator demonstrates plain-language explanation cards, deterministic routing to next steps, and curated official resources — while refusing to diagnose, dose, or predict."
          >
            <ul>
              <li>
                Emergency and crisis inputs always come first and return fixed 911/988
                guidance.
              </li>
              <li>
                Plain-language cards preserve every number, unit, timing, warning, and
                negation.
              </li>
              <li>
                Only curated official resources are linked: 988 Lifeline,
                FindTreatment.gov, HRSA health-center finder, MedlinePlus.
              </li>
            </ul>
          </CaseStudyCard>
          <CaseStudyCard
            variant="engineering"
            title="How the slice is built"
            status="implemented"
            summary="A typed FastAPI slice with SQLAlchemy/Alembic models for curated cards, resources, and synthetic navigation plans; deterministic phrase-based safety checks that bypass every optional layer; validation that rejects diagnosis, dose, percentage, and invariance violations; and org-scoped navigator review with append-only audit events."
          >
            <ul>
              <li>
                Crisis bypass is tested to survive database failure — safety guidance
                never depends on storage.
              </li>
              <li>
                No identity, location, DOB, medical-record, or free-form symptom history
                columns exist.
              </li>
              <li>
                Navigators and admins can review and close only their own
                organization&apos;s synthetic plans.
              </li>
            </ul>
          </CaseStudyCard>
        </div>
      </section>

      <section aria-labelledby="haven-citations-title">
        <div className="section-heading">
          <p className="eyebrow">Grounding</p>
          <h2 id="haven-citations-title">Citations and references</h2>
        </div>
        <ul className="evidence-list">
          <li className="evidence-item">
            <a href="https://www.who.int/publications/i/item/9789240029200">
              WHO — Ethics and governance of artificial intelligence for health
            </a>{" "}
            — why health tools must stay transparent and avoid overstating capability.
          </li>
          <li className="evidence-item">
            <a href="https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software">
              FDA — Clinical Decision Support Software guidance
            </a>{" "}
            — informs Haven&apos;s strict non-diagnostic, non-treatment boundary.
          </li>
          <li className="evidence-item">
            <a href="https://988lifeline.org/">988 Suicide &amp; Crisis Lifeline</a> — the
            official U.S. crisis line surfaced by every crisis path.
          </li>
          <li className="evidence-item">
            <a href="https://health.gov/our-work/national-health-initiatives/health-literacy">
              HHS — Health literacy resources
            </a>{" "}
            — informs the plain-language card approach.
          </li>
        </ul>
      </section>

      <section className="boundaries" aria-labelledby="haven-boundaries-title">
        <h2 id="haven-boundaries-title">What Haven deliberately does not do</h2>
        <ul>
          <li>No diagnosis, treatment, medication, dose, risk percentage, or prognosis.</li>
          <li>No real users, patient accounts, live integrations, or production deployment.</li>
          <li>No storage of identity, location, medical history, or free-form symptom text.</li>
          <li>No monitoring, alerting, or contacting anyone on a visitor&apos;s behalf.</li>
          <li>No claim of HIPAA compliance, clinical review, or healthcare partnership.</li>
        </ul>
      </section>
    </PageShell>
  );
}
