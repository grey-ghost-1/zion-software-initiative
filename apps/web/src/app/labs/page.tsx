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

      <section aria-labelledby="labs-paths-title">
        <h2 id="labs-paths-title">Explore the lab</h2>
        <div className="card-grid">
          <article>
            <h3>Interoperability roadmap</h3>
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
