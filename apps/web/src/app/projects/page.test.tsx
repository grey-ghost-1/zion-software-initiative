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

  it("shows both an engineering and an impact case study without unsupported claims", () => {
    render(<ProjectsPage />);

    expect(screen.getAllByText("Engineering case study").length).toBe(3);
    expect(screen.getByText("Impact case study")).toBeVisible();
    expect(screen.getAllByText("Implemented").length).toBeGreaterThan(0);
    expect(
      screen.getByText(/no deployed service, aid provision, real user, partner/i),
    ).toBeVisible();
    expect(screen.getByRole("link", { name: "Open the Harbor case study" })).toHaveAttribute(
      "href",
      "/harbor",
    );
    for (const forbidden of ["Haven", "Beacon", "Labs"]) {
      expect(screen.queryByText(forbidden)).not.toBeInTheDocument();
    }
  });
});
