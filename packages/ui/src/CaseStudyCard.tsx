import type { ReactNode } from "react";
import { StatusBadge, type WorkStatus } from "./StatusBadge";

/**
 * Case studies come in two flavors for Zion's dual audience: a public-interest
 * "impact" framing and a technical "engineering" framing of the same
 * underlying work. Both variants share one primitive so status and evidence
 * links stay consistent everywhere they appear.
 */
export type CaseStudyVariant = "impact" | "engineering";

export interface CaseStudyCardProps {
  variant: CaseStudyVariant;
  title: string;
  status: WorkStatus;
  summary: string;
  detailsHref?: string;
  detailsLabel?: string;
  children?: ReactNode;
}

const VARIANT_EYEBROW: Record<CaseStudyVariant, string> = {
  impact: "Impact case study",
  engineering: "Engineering case study",
};

export function CaseStudyCard({
  variant,
  title,
  status,
  summary,
  detailsHref,
  detailsLabel,
  children,
}: CaseStudyCardProps) {
  return (
    <article className={`case-study-card case-study-card--${variant}`}>
      <p className="case-study-card__eyebrow">{VARIANT_EYEBROW[variant]}</p>
      <div className="case-study-card__heading">
        <h3>{title}</h3>
        <StatusBadge status={status} />
      </div>
      <p className="case-study-card__summary">{summary}</p>
      {children}
      {detailsHref ? (
        <a
          className="case-study-card__link"
          href={detailsHref}
          target={detailsHref.startsWith("http") ? "_blank" : undefined}
          rel={detailsHref.startsWith("http") ? "noopener noreferrer" : undefined}
        >
          {detailsLabel ?? "View evidence"}
        </a>
      ) : null}
    </article>
  );
}
