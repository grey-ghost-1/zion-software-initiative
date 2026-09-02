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

  it("names only the built demonstration and links to it truthfully", () => {
    render(<InitiativesPage />);

    expect(screen.getByText("Working demonstration")).toBeVisible();
    const beaconLink = screen.getByRole("link", { name: "Beacon" });
    expect(beaconLink).toHaveAttribute("href", "/initiatives/beacon");
    expect(screen.getByText(/fabricated fixture data only/i)).toBeVisible();
    for (const forbidden of ["Haven"]) {
      expect(screen.queryByText(forbidden)).not.toBeInTheDocument();
    }
  });
});
