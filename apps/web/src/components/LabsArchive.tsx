"use client";

import { useMemo, useState, type ReactNode } from "react";
import type { LabProject, LabsArchive, SecondaryLabCategory } from "@/lib/labs";
import {
  formatValidationStatus,
  getFeaturedLabs,
  getSecondaryLabsByCategory,
  SECONDARY_CATEGORY_ORDER,
} from "@/lib/labs";

interface LabsArchiveProps {
  archive: LabsArchive;
}

const CATEGORY_LABELS: Record<SecondaryLabCategory, string> = {
  "software/automation": "Software automation",
  "defensive security": "Defensive security",
  "IT support": "IT support",
  "networking/systems": "Networking/systems",
};

function ExternalLink({
  href,
  children,
}: Readonly<{
  href: string;
  children: ReactNode;
}>) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  );
}

function joinAsSentence(items: string[]): string {
  return items.join("; ");
}

function LabCard({
  project,
  featured = false,
}: Readonly<{
  project: LabProject;
  featured?: boolean;
}>) {
  return (
    <article className={`lab-card${featured ? " lab-card--featured" : ""}`}>
      <div className="lab-card__heading">
        <div>
          <p className="lab-card__eyebrow">
            {featured ? "Featured flagship" : CATEGORY_LABELS[project.category as SecondaryLabCategory]}
          </p>
          <h3>{project.name}</h3>
        </div>
        <span className="lab-chip">{formatValidationStatus(project.validation.status)}</span>
      </div>
      <p className="lab-card__summary">{project.summary}</p>
      <p className="lab-card__meta">
        <strong>Relationship:</strong> {project.relationship}
        <br />
        <strong>Source:</strong> <code>{project.source.path}</code>
      </p>
      <p className="lab-card__facts">
        <strong>Capabilities:</strong> {joinAsSentence(project.features)}.
      </p>
      <p className="lab-card__facts">
        <strong>Limitations:</strong> {joinAsSentence(project.limitations)}.
      </p>
      <p className="lab-card__facts lab-card__facts--validation">
        <strong>Validation:</strong> {project.validation.notes}
      </p>
      <div className="lab-card__links">
        <ExternalLink href={project.source.immutableUrl}>Immutable source</ExternalLink>
        {project.evidenceUrls.map((href) => (
          <ExternalLink key={href} href={href}>
            {href.includes("project-evidence.json") ? "Audited inventory" : "Project archive page"}
          </ExternalLink>
        ))}
      </div>
    </article>
  );
}

export function LabsArchive({ archive }: LabsArchiveProps) {
  const featuredLabs = useMemo(() => getFeaturedLabs(archive), [archive]);
  const [category, setCategory] = useState<SecondaryLabCategory | "all">("all");
  const groupedSecondaryLabs = useMemo(
    () => getSecondaryLabsByCategory(archive, category),
    [archive, category],
  );
  const visibleSecondaryCount = groupedSecondaryLabs.reduce(
    (count, group) => count + group.projects.length,
    0,
  );
  const validation = archive.validationSnapshot;

  return (
    <>
      <section className="page-hero labs-hero" aria-labelledby="labs-title">
        <p className="eyebrow">External prior work archive</p>
        <h1 id="labs-title">Zion Labs</h1>
        <p className="page-intro">
          Prior work by Justin Wimmer, originally published in the Batcomputer Portfolio.
          Zion Software Initiative provides an external reference and does not claim
          operational hosting.
        </p>
        <p className="labs-intro">
          This page is a checked-in, audited snapshot of 23 prior project pages: four
          featured flagships and 19 smaller labs grouped by category, with no runtime GitHub
          calls and no copied Batcomputer assets.
        </p>
        <div className="labs-links">
          <ExternalLink href={archive.sourceSnapshot.inventoryUrl}>Audited inventory</ExternalLink>
          <ExternalLink href={archive.sourceSnapshot.ciRunUrl}>Exact Linux CI run</ExternalLink>
        </div>
      </section>

      <section className="labs-validation" aria-labelledby="validation-title">
        <div className="section-heading">
          <p className="eyebrow">Validation snapshot</p>
          <h2 id="validation-title">Exact counts from the audited snapshot</h2>
        </div>
        <dl className="labs-stats">
          <div>
            <dt>Project pages</dt>
            <dd>{validation.projectCount}</dd>
          </div>
          <div>
            <dt>Featured flagships</dt>
            <dd>{validation.flagshipCount}</dd>
          </div>
          <div>
            <dt>Secondary labs</dt>
            <dd>{validation.secondaryCount}</dd>
          </div>
          <div>
            <dt>Retained legacy folders</dt>
            <dd>{validation.retainedLegacyFolders}</dd>
          </div>
          <div>
            <dt>Passing CI total</dt>
            <dd>{validation.passingTotal}</dd>
          </div>
        </dl>
        <p className="labs-validation__note">
          CI split: {validation.ciTotals
            .map((item) => `${item.tests} ${item.label}`)
            .join(" + ")}
          . Secondary split: {Object.entries(validation.secondaryByCategory)
            .sort(
              ([left], [right]) =>
                SECONDARY_CATEGORY_ORDER.indexOf(left as SecondaryLabCategory) -
                SECONDARY_CATEGORY_ORDER.indexOf(right as SecondaryLabCategory),
            )
            .map(([label, count]) => `${count} ${label}`)
            .join(", ")}
          .
        </p>
      </section>

      <section className="labs-flagships" aria-labelledby="flagships-title">
        <div className="section-heading">
          <p className="eyebrow">Featured flagships</p>
          <h2 id="flagships-title">Four prior flagship projects</h2>
        </div>
        <div className="labs-card-grid">
          {featuredLabs.map((project) => (
            <LabCard key={project.id} project={project} featured />
          ))}
        </div>
      </section>

      <section className="labs-secondary" aria-labelledby="secondary-title">
        <div className="section-heading">
          <p className="eyebrow">Grouped smaller labs</p>
          <h2 id="secondary-title">Nineteen secondary labs, filterable by category</h2>
        </div>
        <div className="labs-filters" role="toolbar" aria-label="Secondary lab filters">
          <button
            type="button"
            className="labs-filter-button"
            aria-pressed={category === "all"}
            onClick={() => setCategory("all")}
          >
            All
          </button>
          {SECONDARY_CATEGORY_ORDER.map((item) => (
            <button
              key={item}
              type="button"
              className="labs-filter-button"
              aria-pressed={category === item}
              onClick={() => setCategory(item)}
            >
              {CATEGORY_LABELS[item]}
            </button>
          ))}
        </div>
        <p className="labs-results" role="status">
          Showing {visibleSecondaryCount} secondary lab{visibleSecondaryCount === 1 ? "" : "s"}.
        </p>
        <div className="labs-group-stack">
          {groupedSecondaryLabs.map((group) => (
            <section key={group.category} aria-labelledby={`secondary-${group.category}`}>
              <h3 id={`secondary-${group.category}`}>{CATEGORY_LABELS[group.category]}</h3>
              <div className="labs-card-grid">
                {group.projects.map((project) => (
                  <LabCard key={project.id} project={project} />
                ))}
              </div>
            </section>
          ))}
        </div>
      </section>

      <section className="labs-boundary" aria-labelledby="boundary-title">
        <h2 id="boundary-title">Boundary and reuse notice</h2>
        <p>
          This archive is an external reference only. It does not host Batcomputer media,
          does not copy Batcomputer styling, and does not claim operational hosting of the
          prior work.
        </p>
      </section>
    </>
  );
}
