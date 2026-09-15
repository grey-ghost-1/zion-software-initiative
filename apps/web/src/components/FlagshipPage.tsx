import type { ReactNode } from "react";
import { StatusBadge } from "@zion/ui";
import { PageShell } from "./PageShell";
import type { FlagshipModule } from "@/content/flagships";

interface FlagshipPageProps {
  module: FlagshipModule;
  safetyNotice?: ReactNode;
  demo: ReactNode;
}

export function FlagshipPage({ module, safetyNotice, demo }: FlagshipPageProps) {
  return (
    <PageShell active="flagships">
      <section className="page-hero" aria-labelledby={`${module.id}-title`}>
        <p className="eyebrow">{module.descriptor}</p>
        <h1 id={`${module.id}-title`}>{module.name}</h1>
        <p className="page-intro">{module.purpose}</p>
        <p>
          <StatusBadge status={module.status.implementation} label={module.status.label} />{" "}
          <strong>{module.status.operationalLabel}</strong>
        </p>
      </section>

      {safetyNotice}

      <section aria-labelledby={`${module.id}-purpose`}>
        <h2 id={`${module.id}-purpose`}>Module Purpose</h2>
        <p>{module.purpose}</p>
      </section>

      <section aria-labelledby={`${module.id}-fit`}>
        <h2 id={`${module.id}-fit`}>How it fits Zion</h2>
        <p>{module.fit}</p>
      </section>

      <section aria-labelledby={`${module.id}-architecture`}>
        <h2 id={`${module.id}-architecture`}>Architecture Summary</h2>
        <p>{module.architecture}</p>
      </section>

      <section className="boundaries" aria-labelledby={`${module.id}-boundaries`}>
        <h2 id={`${module.id}-boundaries`}>Boundaries and Limitations</h2>
        <ul>
          {module.boundaries.map((boundary) => (
            <li key={boundary}>{boundary}</li>
          ))}
        </ul>
      </section>

      <section aria-labelledby={`${module.id}-demo`}>
        <div className="section-heading">
          <p className="eyebrow">Inspectable workflow</p>
          <h2 id={`${module.id}-demo`}>Demo and Evidence</h2>
        </div>
        {demo}
        <h3>Repository evidence</h3>
        <ul className="evidence-list">
          {module.evidence
            .filter((link) => link.href !== module.route)
            .map((link) => (
              <li className="evidence-item" key={link.href}>
                <a href={link.href}>{link.label}</a>
              </li>
            ))}
        </ul>
      </section>

      <section aria-labelledby={`${module.id}-story`}>
        <h2 id={`${module.id}-story`}>Interview Story</h2>
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
      </section>
    </PageShell>
  );
}
