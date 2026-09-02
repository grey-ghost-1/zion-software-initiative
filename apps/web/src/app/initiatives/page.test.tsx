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

  it("links the Haven and Beacon demonstrations truthfully", () => {
    render(<InitiativesPage />);

    expect(screen.getByRole("link", { name: /haven — health-access navigation/i })).toHaveAttribute(
      "href",
      "/initiatives/haven",
    );
    expect(
      screen.getByRole("link", { name: /beacon — coastal-storm readiness workflow/i }),
    ).toHaveAttribute("href", "/initiatives/beacon");
    expect(screen.getAllByText("Working demonstration").length).toBeGreaterThan(0);
    expect(screen.getByText(/non-diagnostic health-access navigation/i)).toBeVisible();
    expect(screen.getByText(/synthetic, deterministic workflow demo/i)).toBeVisible();
  });
});
