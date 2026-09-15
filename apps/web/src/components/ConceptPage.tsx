import { StatusBadge } from "@zion/ui";
import type { ConceptModule } from "@/content/concepts";
import { PageShell } from "./PageShell";

export function ConceptSections({ concept }: { concept: ConceptModule }) {
  return (
    <>
      <section aria-labelledby={`${concept.id}-purpose`}>
        <h2 id={`${concept.id}-purpose`}>Module purpose</h2>
        <p>{concept.purpose}</p>
      </section>
      <section aria-labelledby={`${concept.id}-fit`}>
        <h2 id={`${concept.id}-fit`}>How it fits Zion</h2>
        <p>{concept.fit}</p>
      </section>
      <section aria-labelledby={`${concept.id}-architecture`}>
        <h2 id={`${concept.id}-architecture`}>Architecture summary</h2>
        <p>{concept.architecture}</p>
      </section>
      <section className="boundaries" aria-labelledby={`${concept.id}-safety`}>
        <h2 id={`${concept.id}-safety`}>Safety boundaries</h2>
        <p>
          Concept / roadmap only; unimplemented and non-operational. Synthetic-only:
          any future examples must be fabricated. Do not submit real PHI, patient records,
          or other personal data. This scaffold has no data-entry or upload workflow.
        </p>
        <p>
          No live clinical operation, real EHR connectivity, actual HL7/FHIR exchange,
          SMART on FHIR integration, standards conformance, certification, HIPAA compliance,
          diagnosis or treatment, production deployment, or existing GitHub implementation
          is claimed. No functional implementation, runtime tests, external demo, or
          prior-work evidence exists for this concept; web scaffold checks are not
          implementation evidence.
        </p>
      </section>
      <section aria-labelledby={`${concept.id}-github`}>
        <h2 id={`${concept.id}-github`}>GitHub links placeholder</h2>
        <p>
          No implementation repository/evidence link exists yet. The shared View source
          link points to Zion&apos;s repository, not an implementation of this concept.
        </p>
      </section>
      <section aria-labelledby={`${concept.id}-story`}>
        <h2 id={`${concept.id}-story`}>Interview story placeholder</h2>
        <p>Content will be added only after implementation and validation.</p>
      </section>
      <section aria-labelledby={`${concept.id}-highlights`}>
        <h2 id={`${concept.id}-highlights`}>Technical highlights placeholder</h2>
        <p>Content will be added only after implementation and validation.</p>
      </section>
    </>
  );
}

export function ConceptPage({
  concept,
  area,
}: {
  concept: ConceptModule;
  area: "flagships" | "labs";
}) {
  return (
    <PageShell active={area} labsSection={area === "labs" ? "interoperability" : undefined}>
      <section className="page-hero" aria-labelledby={`${concept.id}-title`}>
        <p className="eyebrow">Roadmap-only web scaffold</p>
        <h1 id={`${concept.id}-title`}>{concept.name}</h1>
        <p>
          <StatusBadge status="planned" label="Concept / roadmap" />{" "}
          <strong>Unimplemented; non-operational; synthetic-only.</strong>
        </p>
        <p className="page-intro">
          This is a static concept page, not a working demonstration or implementation.
        </p>
      </section>
      <ConceptSections concept={concept} />
    </PageShell>
  );
}
