import type { Metadata } from "next";
import { StatusBadge } from "@zion/ui";
import { PageShell } from "@/components/PageShell";
import { loadEvidenceClaims } from "@/lib/evidence";

export const metadata: Metadata = {
  title: "Evidence · Zion Software Initiative",
};

const REPO_BLOB_BASE = "https://github.com/grey-ghost-1/zion-software-initiative/blob/main/";

export default function EvidencePage() {
  const claims = loadEvidenceClaims();

  return (
    <PageShell>
      <section className="page-hero" aria-labelledby="evidence-title">
        <p className="eyebrow">Inspectable claims</p>
        <h1 id="evidence-title">Every implemented claim, linked to proof</h1>
        <p className="page-intro">
          This list is generated from the same{" "}
          <a
            href={`${REPO_BLOB_BASE}docs/evidence/inventory.json`}
            target="_blank"
            rel="noopener noreferrer"
          >
            evidence inventory
          </a>{" "}
          the repository&apos;s own tests validate, so it cannot drift from what is
          actually implemented.
        </p>
      </section>

      <section aria-labelledby="claims-title">
        <h2 id="claims-title" className="visually-hidden">
          Implemented claims
        </h2>
        <ul className="evidence-list">
          {claims.map((claim) => (
            <li key={claim.id} className="evidence-item">
              <div className="evidence-item__heading">
                <h3>{claim.claim}</h3>
                <StatusBadge status={claim.status} />
              </div>
              <p className="evidence-item__verified">Verified by: {claim.verified_by}</p>
              <a
                href={`${REPO_BLOB_BASE}${claim.evidence}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                View evidence: {claim.evidence}
              </a>
            </li>
          ))}
        </ul>
      </section>
    </PageShell>
  );
}
