import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import InitiativesPage from "./page";

describe("Initiatives page", () => {
  it("marks Initiatives as the current nav page and keeps one h1", () => {
    render(<InitiativesPage />);

    const nav = screen.getByRole("navigation", { name: "Primary" });
    expect(within(nav).getByRole("link", { name: "Flagships" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });

  it("links the two Zion flagships truthfully", () => {
    render(<InitiativesPage />);

    expect(screen.getByRole("link", { name: /care for the vulnerable/i })).toHaveAttribute(
      "href",
      "/harbor",
    );
    expect(
      screen.getByRole("link", { name: /healing & health access/i }),
    ).toHaveAttribute(
      "href",
      "/initiatives/haven",
    );
    expect(screen.getAllByText("Working demonstration").length).toBeGreaterThan(0);
    expect(screen.getByText(/two implemented Zion flagships/i)).toBeVisible();
    expect(screen.getByText(/Community Aid Hub — Harbor — shows needs, matching/i)).toBeVisible();
    expect(screen.getByText(/Health Navigator and Care Routing Directory — Haven/i)).toBeVisible();
  });
});
