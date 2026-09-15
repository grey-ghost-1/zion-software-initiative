import type { Metadata } from "next";
import { StatusBadge } from "@zion/ui";
import { PageShell } from "@/components/PageShell";

export const metadata: Metadata = {
  title: "Interoperability Lab Roadmap · Zion Software Initiative",
  description: "Unimplemented interoperability concepts, documented without capability claims.",
};

const concepts = [
  {
    name: "FHIR Dashboard",
    question:
      "Could a future synthetic-data interface make standards-shaped resource relationships understandable without implying clinical authority?",
  },
  {
    name: "HL7-to-FHIR Converter",
    question:
      "Could a future offline teaching tool explain mapping tradeoffs using fabricated examples and explicit validation failures?",
  },
  {
    name: "EHR Workflow Simulator",
    question:
      "Could a future simulator help engineers study human review points without connecting to a real care environment?",
  },
] as const;

export default function InteroperabilityRoadmapPage() {
  return (
    <PageShell active="initiatives">
      <section className="page-hero" aria-labelledby="interoperability-title">
        <p className="eyebrow">Roadmap only · no implementation</p>
        <h1 id="interoperability-title">Interoperability lab concepts</h1>
        <p className="page-intro">
          <StatusBadge status="planned" label="Unimplemented concepts" /> An audit of the
          immutable Batcomputer snapshot found no implementation or tests for the three
          concepts below. They are documented only as possible learning directions.
        </p>
      </section>

      <section aria-labelledby="concepts-title">
        <div className="section-heading">
          <p className="eyebrow">Zero implementation and zero tests</p>
          <h2 id="concepts-title">Questions, not project claims</h2>
        </div>
        <div className="card-grid">
          {concepts.map((concept) => (
            <article key={concept.name}>
              <h3>{concept.name}</h3>
              <p>{concept.question}</p>
              <p>
                <strong>Status:</strong> not started; no code, tests, route, integration, or
                deployment exists.
              </p>
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
          interoperability service. No Batcomputer content or assets are copied here.
        </p>
      </section>
    </PageShell>
  );
}
