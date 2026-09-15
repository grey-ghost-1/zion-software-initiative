import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PageShell, type PageId } from "./PageShell";

describe("shared page shell", () => {
  it.each<PageId | undefined>([undefined, "mission", "architecture", "flagships", "labs"])(
    "preserves primary navigation and exactly one unchanged footer on %s",
    (active) => {
      render(<PageShell active={active}><h1>Page</h1></PageShell>);

      const nav = screen.getByRole("navigation", { name: "Primary" });
      const topLinks = nav.querySelectorAll(":scope > ul > li > a");
      expect(Array.from(topLinks, (link) => link.textContent)).toEqual([
        "Mission", "Architecture", "Flagships", "Zion Labs",
      ]);
      expect(screen.getAllByRole("navigation")).toHaveLength(1);
      expect(screen.getByRole("link", { name: "Skip to main content" })).toHaveAttribute(
        "href", "#main-content",
      );
      expect(screen.getByRole("main")).toHaveAttribute("id", "main-content");
      expect(screen.getAllByRole("contentinfo")).toHaveLength(1);
      const footer = screen.getByRole("contentinfo");
      const disclosure = within(footer).getByRole("complementary", { name: "Global disclosure" });
      expect(within(disclosure).getByRole("heading")).toHaveTextContent("Global disclosure");
      expect(disclosure.querySelector("p")?.textContent?.replace(/\s+/g, " ").trim()).toBe(
        "This platform uses synthetic data, does not diagnose or treat, does not collect real health information, and is not an operational public service. There is no hosted production deployment, real-user or partner use, or measured field outcome.",
      );
    },
  );

  it.each(["interoperability", "prior-work"] as const)(
    "exposes accessible nested Labs links and identifies the %s section",
    (labsSection) => {
      render(<PageShell active="labs" labsSection={labsSection}><h1>Lab</h1></PageShell>);
      const list = screen.getByRole("list", { name: "Zion Labs sections" });
      expect(list.closest("details")).toHaveAttribute("open");
      expect(list.closest("nav")).toBe(screen.getByRole("navigation", { name: "Primary" }));
      expect(within(list).getAllByRole("link").map((link) => link.textContent)).toEqual([
        "Interoperability Engineering", "Prior Audited Work",
      ]);
      expect(within(list).getByRole("link", { name: "Interoperability Engineering" }))
        .toHaveAttribute("href", "/labs/interoperability");
      expect(within(list).getByRole("link", { name: "Prior Audited Work" }))
        .toHaveAttribute("href", "/labs/prior-work");
      expect(within(list).getByRole("link", { current: "location" })).toHaveAttribute(
        "href", `/labs/${labsSection}`,
      );
    },
  );

  it("uses a native disclosure that can open outside Labs without a hover interaction", () => {
    render(<PageShell active="mission"><h1>Mission</h1></PageShell>);
    const summary = screen.getByText("Zion Labs sections", { selector: "summary" });
    const disclosure = summary.closest("details")!;
    expect(disclosure).not.toHaveAttribute("open");
    fireEvent.click(summary);
    expect(disclosure).toHaveAttribute("open");
    fireEvent.click(summary);
    expect(disclosure).not.toHaveAttribute("open");
  });
});
