import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ProjectsPage from "./page";

describe("Projects page", () => {
  it("marks Projects as the current nav page and keeps one h1", () => {
    render(<ProjectsPage />);

    const nav = screen.getByRole("navigation", { name: "Primary" });
    expect(within(nav).getByRole("link", { name: "Projects" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });

  it("surfaces the three Zion project routes before the supporting foundation cards", () => {
    render(<ProjectsPage />);

    const projectNav = screen.getByRole("navigation", { name: "Project pages" });
    for (const [label, href] of [
      ["Community Aid Hub", "/projects/community-aid-hub"],
      ["Health Navigator", "/projects/health-navigator"],
      ["Humanitarian Automation Pipeline", "/projects/humanitarian-automation-pipeline"],
      ["Initiatives", "/initiatives"],
    ]) {
      expect(within(projectNav).getByRole("link", { name: label })).toHaveAttribute(
        "href",
        href,
      );
    }

    expect(screen.getByText("Three first-class project pages, one shared foundation")).toBeVisible();
    expect(screen.getAllByText("Community Aid Hub").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Health Navigator").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Humanitarian Automation Pipeline").length).toBeGreaterThan(0);
    expect(screen.getByText("Shared platform foundation")).toBeVisible();
    expect(screen.getByText("Accessible dual-audience web shell")).toBeVisible();
    expect(screen.getAllByText("Impact case study").length).toBe(3);
    expect(screen.getAllByText("Engineering case study").length).toBe(2);
  });
});
