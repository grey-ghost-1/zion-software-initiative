import Link from "next/link";
import type { ReactNode } from "react";

export type PageId = "mission" | "architecture" | "flagships" | "labs";

interface NavItem {
  id: PageId;
  href: string;
  label: string;
}

const NAV_ITEMS: NavItem[] = [
  { id: "mission", href: "/mission", label: "Mission" },
  { id: "architecture", href: "/architecture", label: "Architecture" },
  { id: "flagships", href: "/flagships", label: "Flagships" },
  { id: "labs", href: "/labs", label: "Zion Labs" },
];

interface PageShellProps {
  active?: PageId;
  labsSection?: "interoperability" | "prior-work";
  children: ReactNode;
}

/**
 * Shared chrome for every page: skip link, header with primary navigation,
 * the `main` landmark, and a footer. Kept as one component so navigation
 * semantics (landmarks, skip link, `aria-current`) stay identical everywhere.
 */
export function PageShell({ active, labsSection, children }: PageShellProps) {
  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <header className="site-header">
        <Link className="brand" href="/" aria-label="Zion home">
          Zion
        </Link>
        <nav className="site-nav" aria-label="Primary">
          <ul>
            {NAV_ITEMS.map((item) => (
              <li key={item.id}>
                <Link href={item.href} aria-current={item.id === active ? "page" : undefined}>
                  {item.label}
                </Link>
                {item.id === "labs" && (
                  <details className="labs-subnav" open={active === "labs"}>
                    <summary>Zion Labs sections</summary>
                    <ul aria-label="Zion Labs sections">
                      <li>
                        <Link
                          href="/labs/interoperability"
                          aria-current={labsSection === "interoperability" ? "location" : undefined}
                        >
                          Interoperability Engineering
                        </Link>
                      </li>
                      <li>
                        <Link
                          href="/labs/prior-work"
                          aria-current={labsSection === "prior-work" ? "location" : undefined}
                        >
                          Prior Audited Work
                        </Link>
                      </li>
                    </ul>
                  </details>
                )}
              </li>
            ))}
          </ul>
        </nav>
        <a
          className="repository-link"
          href="https://github.com/grey-ghost-1/zion-software-initiative"
          target="_blank"
          rel="noopener noreferrer"
        >
          View source
        </a>
      </header>
      <main id="main-content">{children}</main>
      <footer>
        <aside aria-labelledby="global-disclosure-title">
          <h2 id="global-disclosure-title">Global disclosure</h2>
          <p>
            This platform uses synthetic data, does not diagnose or treat, does not collect
            real health information, and is not an operational public service. There is no
            hosted production deployment, real-user or partner use, or measured field outcome.
          </p>
        </aside>
        <p>Zion Software Initiative — foundation stage</p>
      </footer>
    </>
  );
}
