import type { Metadata } from "next";
import Link from "next/link";
import { PageShell } from "@/components/PageShell";

export const metadata: Metadata = {
  title: "Zion Labs · Zion Software Initiative",
  description: "Bounded research concepts and attributed prior-work evidence.",
};

export default function LabsPage() {
  return (
    <PageShell active="labs">
      <section className="page-hero" aria-labelledby="labs-title">
        <p className="eyebrow">Research with explicit claim boundaries</p>
        <h1 id="labs-title">Zion Labs</h1>
        <p className="page-intro">
          Labs separates future learning questions and independently attributed prior work
          from Zion&apos;s implemented flagships. A listing here is not a Zion capability.
        </p>
      </section>

      <section aria-labelledby="labs-purpose">
        <h2 id="labs-purpose">Module purpose</h2>
        <p>Provide a bounded catalog of learning concepts and attributed external evidence.</p>
      </section>
      <section aria-labelledby="labs-fit">
        <h2 id="labs-fit">How it fits Zion</h2>
        <p>Keep roadmap questions and prior audited work distinct from Harbor/Haven implementation evidence.</p>
      </section>
      <section aria-labelledby="labs-architecture">
        <h2 id="labs-architecture">Architecture summary</h2>
        <p>Static App Router pages link concept scaffolds and an immutable external evidence inventory; Labs has no operational integration service.</p>
      </section>
      <section className="boundaries" aria-labelledby="labs-safety">
        <h2 id="labs-safety">Safety boundaries</h2>
        <p>Interoperability entries are Concept / roadmap only: unimplemented, non-operational, synthetic-only. No clinical operation, real PHI, EHR connectivity, HL7/FHIR exchange, conformance, HIPAA compliance, diagnosis or treatment, or production deployment is claimed.</p>
      </section>

      <section aria-labelledby="labs-paths-title">
        <h2 id="labs-paths-title">Explore the lab</h2>
        <div className="card-grid">
          <article>
            <h3>Interoperability Engineering</h3>
            <p>Three unimplemented learning concepts, stated only as questions.</p>
            <Link href="/labs/interoperability">Read the concept roadmap</Link>
          </article>
          <article>
            <h3>Prior work inventory</h3>
            <p>An attributed index backed by an audited, immutable evidence snapshot.</p>
            <Link href="/labs/prior-work">Review prior-work evidence</Link>
          </article>
        </div>
      </section>
    </PageShell>
  );
}
