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
          An &quot;initiative&quot; is a bounded public-interest software exploration.
          Harbor now provides one synthetic, inspectable prototype; it is not a deployed
          service or evidence of real-world impact.
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
          <StatusBadge status="implemented" label="Synthetic prototype" />{" "}
          <a href="/harbor">Harbor</a> demonstrates transparent matching, coordinator
          approval, capacity reservation, and audit with synthetic records only. Haven
          and Beacon remain unimplemented directions without a timeline.
        </p>
      </section>
    </PageShell>
  );
}
