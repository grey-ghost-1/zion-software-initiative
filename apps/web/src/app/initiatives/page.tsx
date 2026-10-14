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
        <h1 id="initiatives-title">How Zion approaches initiatives</h1>
        <p className="page-intro">
          An &quot;initiative&quot; is a proposed piece of public-interest software Zion
          might build. None is published or under active development yet in this
          repository — this page describes the approach, not a product.
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

      <section className="status-section" aria-labelledby="status-title">
        <h2 id="status-title">Current status</h2>
        <p>
          <StatusBadge status="planned" /> No specific initiative has a name, scope, or
          timeline in this repository yet. What exists today is the shared foundation
          described on the <a href="/projects">Projects</a> page.
        </p>
      </section>
    </PageShell>
  );
}
