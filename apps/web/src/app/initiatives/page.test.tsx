import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import InitiativesPage from "./page";

describe("Initiatives page", () => {
  it("marks Initiatives as the current nav page and keeps one h1", () => {
    render(<InitiativesPage />);

    const nav = screen.getByRole("navigation", { name: "Primary" });
    expect(within(nav).getByRole("link", { name: "Initiatives" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });

  it("describes the approach truthfully without naming an unbuilt product", () => {
    render(<InitiativesPage />);

    expect(
      screen.getByText(/none is published or under active development yet/i),
    ).toBeVisible();
    expect(screen.getByText("Planned")).toBeVisible();
    for (const forbidden of ["Harbor", "Haven", "Beacon"]) {
      expect(screen.queryByText(forbidden)).not.toBeInTheDocument();
    }
  });
});
