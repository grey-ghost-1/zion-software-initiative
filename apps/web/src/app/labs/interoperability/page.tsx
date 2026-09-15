import type { Metadata } from "next";
import { StatusBadge } from "@zion/ui";
import { PageShell } from "@/components/PageShell";
import { ConceptSections } from "@/components/ConceptPage";
import { interoperabilityConcepts } from "@/content/concepts";

export const metadata: Metadata = {
  title: "Interoperability Lab Roadmap · Zion Software Initiative",
  description: "Unimplemented interoperability concepts, documented without capability claims.",
};

export default function InteroperabilityRoadmapPage() {
  return (
    <PageShell active="labs" labsSection="interoperability">
      <section className="page-hero" aria-labelledby="interoperability-title">
        <p className="eyebrow">Roadmap only · no implementation</p>
        <h1 id="interoperability-title">Interoperability lab concepts</h1>
        <p className="page-intro">
          <StatusBadge status="planned" label="Concept / roadmap" />{" "}
          <strong>Unimplemented; non-operational; synthetic-only.</strong> An audit of the
          immutable Batcomputer snapshot found no implementation or tests for the three
          concepts below. They are documented only as possible learning directions.
        </p>
      </section>

      <section aria-labelledby="concepts-title">
        <div className="section-heading">
          <p className="eyebrow">Zero functional implementation or runtime tests</p>
          <h2 id="concepts-title">Questions, not project claims</h2>
        </div>
        <div className="card-grid">
          {interoperabilityConcepts.map((concept) => (
            <article key={concept.name}>
              <h3>{concept.name}</h3>
              <p>{concept.purpose}</p>
              <p>
                <strong>Status:</strong> Concept / roadmap; no functional implementation,
                runtime tests, integration, or deployment exists. Only a static concept
                route and web scaffold checks exist.
              </p>
              <a href={concept.route}>Read the {concept.name} concept</a>
            </article>
          ))}
        </div>
      </section>

      <section className="boundaries" aria-labelledby="interop-boundaries-title">
        <h2 id="interop-boundaries-title">Claims this roadmap does not make</h2>
        <p>
          Zion has no real EHR connectivity, HL7 or FHIR exchange, SMART on FHIR
          integration, standards conformance, certification, clinical use, HIPAA
          compliance, real PHI, diagnosis or treatment capability, or deployed
          interoperability service. These concepts have no functional implementation, runtime tests,
          external demo, or prior-work claim. No Batcomputer content or assets are
          copied here.
        </p>
      </section>
      <ConceptSections
        concept={{
          id: "interoperability",
          name: "Interoperability Engineering",
          route: "/labs/interoperability",
          purpose: "Document three possible synthetic-only learning exercises without claiming working interoperability software.",
          fit: "Zion Labs keeps these research questions separate from the implemented Harbor/Haven demonstrations and from attributed prior audited work.",
          architecture: "This index links static concept pages only. Proposed local fixtures and human-review exercises are roadmap ideas, not implemented services or exchange infrastructure.",
        }}
      />
    </PageShell>
  );
}
