import type { Metadata } from "next";
import { StatusBadge } from "@zion/ui";
import { PageShell } from "@/components/PageShell";

export const metadata: Metadata = {
  title: "Initiatives · Zion Software Initiative",
};

export default function InitiativesPage() {
  return (
    <PageShell active="initiatives">
      <section className="page-hero" aria-labelledby="initiatives-title">
        <p className="eyebrow">Public-interest direction</p>
        <h1 id="initiatives-title">Three original avenues of Zion</h1>
        <p className="page-intro">
          Zion is built around three original avenues of impact. Each avenue is
          synthetic here, but the structure is designed to prove that software can
          heal, protect, and uplift.
        </p>
      </section>

      <section aria-labelledby="approach-title">
        <div className="section-heading">
          <p className="eyebrow">Working principles</p>
          <h2 id="approach-title">What every future initiative must do first</h2>
        </div>
        <div className="card-grid">
          <article>
            <h3>Serve two audiences honestly</h3>
            <p>
              Explain the public-interest problem in plain language while giving
              engineers concrete, inspectable evidence — never one audience hidden
              behind the other.
            </p>
          </article>
          <article>
            <h3>Use only synthetic or curated public data</h3>
            <p>
              No personal, vulnerable-population, health, or location data is
              collected. Demonstrations use synthetic examples so they stay safe to
              publish.
            </p>
          </article>
          <article>
            <h3>Share one platform foundation</h3>
            <p>
              Authentication, organizations, roles, and audit logging are built once,
              here, so a future initiative reuses proven infrastructure instead of
              duplicating it.
            </p>
          </article>
        </div>
      </section>

      <section aria-labelledby="current-title">
        <div className="section-heading">
          <p className="eyebrow">Demonstrations</p>
          <h2 id="current-title">Current initiative demonstrations</h2>
        </div>
        <div className="card-grid">
          <article>
            <h3>
              <a href="/harbor">Care for the Vulnerable</a>
            </h3>
            <p>
              <StatusBadge status="implemented" label="Working demonstration" /> Community
              Aid Hub — Harbor — shows needs, matching, triage, capacity checks,
              volunteer plans, and audit timelines.
            </p>
          </article>
          <article>
            <h3>
              <a href="/initiatives/haven">Healing &amp; Health Access</a>
            </h3>
            <p>
              <StatusBadge status="implemented" label="Working demonstration" /> Health
              Navigator and Care Routing Directory — Haven — simplify navigation with
              non-diagnostic guidance, emergency and crisis routing, plain-language
              cards, and curated resources.
            </p>
          </article>
          <article>
            <h3>
              <a href="/initiatives/beacon">AI Infrastructure, Automation &amp; Empowerment</a>
            </h3>
            <p>
              <StatusBadge status="implemented" label="Working demonstration" /> Humanitarian
              Automation Pipeline and AI Empowerment &amp; Education Suite — Beacon —
              automate coordination with typed steps, policy and provenance checks,
              explainable allocation, and required human approval.
            </p>
          </article>
        </div>
      </section>

      <section className="status-section" aria-labelledby="status-title">
        <h2 id="status-title">Current status</h2>
        <p>
          <StatusBadge status="implemented" label="Working demonstration" /> Harbor,
          Haven, and Beacon are the implemented Zion demonstrations. They map to
          care for the vulnerable, healing &amp; health access, and AI infrastructure,
          automation &amp; empowerment. The shared foundation is described on the{" "}
          <a href="/projects">Projects</a> page.
        </p>
      </section>
    </PageShell>
  );
}
