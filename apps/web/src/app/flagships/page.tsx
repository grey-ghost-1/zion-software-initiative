import type { Metadata } from "next";
import { StatusBadge } from "@zion/ui";
import { PageShell } from "@/components/PageShell";
import { flagshipModules } from "@/content/flagships";
import { beaconConcept } from "@/content/concepts";

export const metadata: Metadata = {
  title: "Flagships · Zion Software Initiative",
  description: "Zion's two implemented, non-operational flagship demonstrations.",
};

export default function FlagshipsPage() {
  return (
    <PageShell active="flagships">
      <section className="page-hero" aria-labelledby="flagships-title">
        <p className="eyebrow">Shipping platform modules</p>
        <h1 id="flagships-title">Harbor and Haven</h1>
        <p className="page-intro">
          Two bounded demonstrations share Zion&apos;s responsible-engineering foundation.
          Each has one canonical case study and demonstration route.
        </p>
      </section>

      <section aria-labelledby="catalog-title">
        <div className="section-heading">
          <p className="eyebrow">Typed content catalog</p>
          <h2 id="catalog-title">Two modules, explicit evidence and boundaries</h2>
        </div>
        <div className="case-study-grid">
          {flagshipModules.map((module) => (
            <article className="case-study-card case-study-card--engineering" key={module.id}>
              <p className="case-study-card__eyebrow">{module.descriptor}</p>
              <h3>{module.name}</h3>
              <p>
                <StatusBadge status={module.status.implementation} label={module.status.label} />{" "}
                <strong>{module.status.operationalLabel}</strong>
              </p>
              <h4>Module purpose</h4>
              <p>{module.purpose}</p>
              <h4>How it fits Zion</h4>
              <p>{module.fit}</p>
              <h4>Architecture summary</h4>
              <p>{module.architecture}</p>
              <h4>Safety boundaries</h4>
              <ul>
                {module.boundaries.map((boundary) => (
                  <li key={boundary}>{boundary}</li>
                ))}
              </ul>
              <h4>Interview story</h4>
              <dl>
                {Object.entries(module.interviewStory).map(([part, detail]) => (
                  <div key={part}>
                    <dt>
                      <strong>{part[0].toUpperCase() + part.slice(1)}</strong>
                    </dt>
                    <dd>{detail}</dd>
                  </div>
                ))}
              </dl>
              <h4>Technical highlights</h4>
              <ul>
                {module.technicalHighlights.map((highlight) => (
                  <li key={highlight}>{highlight}</li>
                ))}
              </ul>
              <h4>Demo and Evidence</h4>
              <ul>
                {module.evidence.map((link) => (
                  <li key={link.href}>
                    <a href={link.href}>{link.label}</a>
                  </li>
                ))}
              </ul>
              <p>
                <a href={module.route}>Open {module.name}</a>
              </p>
            </article>
          ))}
        </div>
      </section>
      <section className="boundaries" aria-labelledby="flagship-roadmap-title">
        <h2 id="flagship-roadmap-title">Separate concept roadmap</h2>
        <h3>Beacon</h3>
        <p>
          <StatusBadge status="planned" label="Concept / roadmap" />{" "}
          Unimplemented, non-operational, synthetic-only governance/workflow concept.
          This is not a third implemented flagship; no Beacon runtime is restored.
        </p>
        <a href={beaconConcept.route}>Read the Beacon concept scaffold</a>
      </section>
    </PageShell>
  );
}
