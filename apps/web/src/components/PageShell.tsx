import Link from "next/link";
import type { ReactNode } from "react";

export type PageId = "home" | "initiatives" | "projects" | "evidence" | "about";

interface NavItem {
  id: PageId;
  href: string;
  label: string;
}

const NAV_ITEMS: NavItem[] = [
  { id: "home", href: "/", label: "Home" },
  { id: "initiatives", href: "/initiatives", label: "Initiatives" },
  { id: "projects", href: "/projects", label: "Projects" },
  { id: "evidence", href: "/evidence", label: "Evidence" },
  { id: "about", href: "/about", label: "About Justin" },
];

interface PageShellProps {
  /** Which nav item is the current page, for `aria-current="page"`. */
  active: PageId;
  children: ReactNode;
}

/**
 * Shared chrome for every page: skip link, header with primary navigation,
 * the `main` landmark, and a footer. Kept as one component so navigation
 * semantics (landmarks, skip link, `aria-current`) stay identical everywhere.
 */
export function PageShell({ active, children }: PageShellProps) {
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
              </li>
            ))}
          </ul>
        </nav>
        <a
          className="repository-link"
          href="https://github.com/grey-ghost-1/zion-software-initiative"
        >
          View source
        </a>
      </header>
      <main id="main-content">{children}</main>
      <footer>
        <p>Zion Software Initiative - Foundation stage</p>
      </footer>
    </>
  );
}
