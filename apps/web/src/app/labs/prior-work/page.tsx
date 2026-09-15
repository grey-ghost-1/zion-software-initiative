import type { Metadata } from "next";
import { PageShell } from "@/components/PageShell";
import archive from "../../../../../../docs/evidence/zion-labs-prior-work.json";

export const metadata: Metadata = {
  title: "Prior Work · Zion Labs",
  description: "Attributed links to an audited, immutable prior-work evidence snapshot.",
};

export default function PriorWorkPage() {
  return (
    <PageShell active="labs">
      <section className="page-hero" aria-labelledby="prior-work-title">
        <p className="eyebrow">Audited external evidence</p>
        <h1 id="prior-work-title">Prior work inventory</h1>
        <p className="page-intro">
          This page is an index of external evidence, not Zion work or a transfer of
          project ownership. It reproduces no Batcomputer branding, source code, project
          copy, or assets.
        </p>
      </section>

      <aside className="status" aria-labelledby="prior-attribution-title">
        <h2 id="prior-attribution-title">Required attribution</h2>
        <p>
          <strong>Creator:</strong> {archive.attribution.creator}.{" "}
          {archive.attribution.origin} No reuse license was identified in the audited
          snapshot; links are provided for evidence and attribution only.
        </p>
      </aside>

      <section aria-labelledby="snapshot-title">
        <h2 id="snapshot-title">Immutable audit snapshot</h2>
        <p>
          Audited {archive.sourceSnapshot.auditedAt} at commit{" "}
          <code>{archive.sourceSnapshot.commit}</code>. Inventory:{" "}
          <a href={archive.sourceSnapshot.inventoryUrl}>immutable evidence file</a>. CI:{" "}
          <a href={archive.sourceSnapshot.ciRunUrl}>recorded workflow run</a>.
        </p>
        <p>
          The snapshot records {archive.validationSnapshot.projectCount} projects and{" "}
          {archive.validationSnapshot.passingTotal} passing checks. Those historical
          results are not Zion tests or Zion implementation evidence.
        </p>
      </section>

      <section aria-labelledby="inventory-title">
        <h2 id="inventory-title">Evidence links</h2>
        <ul className="evidence-list">
          {archive.projects.map((project) => (
            <li className="evidence-item" key={project.id}>
              <a href={project.source.immutableUrl}>{project.name}</a>{" "}
              <span>— {project.category}; {project.tier} inventory entry</span>
            </li>
          ))}
        </ul>
      </section>
    </PageShell>
  );
}
