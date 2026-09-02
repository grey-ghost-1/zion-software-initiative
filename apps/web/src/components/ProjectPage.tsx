import Link from "next/link";
import type { ReactNode } from "react";
import { StatusBadge, type WorkStatus } from "@zion/ui";
import { PageShell } from "./PageShell";

interface RelatedLink {
  href: string;
  label: string;
}

interface EvidenceLink {
  href: string;
  label: string;
  note: string;
}

interface ProjectPageProps {
  active: "projects";
  eyebrow: string;
  slug: string;
  title: string;
  intro: string;
  overview: string;
  status: WorkStatus;
  purpose: string;
  audience: string[];
  features: string[];
  limitations: string[];
  evidence: EvidenceLink[];
  relatedLinks: RelatedLink[];
  children?: ReactNode;
}

export function ProjectPage({
  active,
  eyebrow,
  slug,
  title,
  intro,
  overview,
  status,
  purpose,
  audience,
  features,
  limitations,
  evidence,
  relatedLinks,
  children,
}: ProjectPageProps) {
  return (
    <PageShell active={active}>
      <section className="page-hero project-hero" aria-labelledby={`${slug}-title`}>
        <p className="eyebrow">{eyebrow}</p>
        <h1 id={`${slug}-title`}>{title}</h1>
        <p className="page-intro">
          <StatusBadge status={status} label="Working demonstration" /> {intro}
        </p>
        <p>{overview}</p>
        <nav className="project-nav" aria-label={`${title} links`}>
          {relatedLinks.map((link) => (
            <Link key={link.href} href={link.href}>
              {link.label}
            </Link>
          ))}
        </nav>
      </section>

      <section className="project-section" aria-labelledby={`${slug}-purpose`}>
        <h2 id={`${slug}-purpose`}>Purpose</h2>
        <p>{purpose}</p>
      </section>

      <section className="project-section" aria-labelledby={`${slug}-audience`}>
        <h2 id={`${slug}-audience`}>Audience</h2>
        <ul>
          {audience.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="project-section" aria-labelledby={`${slug}-features`}>
        <h2 id={`${slug}-features`}>Features</h2>
        <ul>
          {features.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="project-section" aria-labelledby={`${slug}-limitations`}>
        <h2 id={`${slug}-limitations`}>Limitations</h2>
        <ul>
          {limitations.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className="project-section" aria-labelledby={`${slug}-evidence`}>
        <h2 id={`${slug}-evidence`}>Evidence</h2>
        <ul className="project-evidence-list">
          {evidence.map((item) => (
            <li key={item.href}>
              <a
                href={item.href}
                target={item.href.startsWith("http") ? "_blank" : undefined}
                rel={item.href.startsWith("http") ? "noopener noreferrer" : undefined}
              >
                {item.label}
              </a>
              <p>{item.note}</p>
            </li>
          ))}
        </ul>
      </section>

      {children}
    </PageShell>
  );
}
