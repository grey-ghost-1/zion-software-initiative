import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import EvidencePage from "./page";
import { loadEvidenceClaims } from "@/lib/evidence";

describe("Evidence page", () => {
  it("marks Evidence as the current nav page and keeps one h1", () => {
    render(<EvidencePage />);

    const nav = screen.getByRole("navigation", { name: "Primary" });
    expect(within(nav).getByRole("link", { name: "Evidence" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });

  it("renders every claim from the evidence inventory with a working evidence link", () => {
    render(<EvidencePage />);

    const claims = loadEvidenceClaims();
    expect(claims.length).toBeGreaterThan(0);

    for (const claim of claims) {
      expect(screen.getByText(claim.claim)).toBeVisible();
      const links = screen.getAllByRole("link", {
        name: `View evidence: ${claim.evidence}`,
      });
      expect(
        links.some(
          (link) =>
            link.getAttribute("href") ===
            `https://github.com/grey-ghost-1/zion-software-initiative/blob/main/${claim.evidence}`,
        ),
      ).toBe(true);
    }
    expect(screen.getAllByText("Implemented").length).toBe(claims.length);
  });
});
