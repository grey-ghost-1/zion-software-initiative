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

  it("links the Haven demonstration without naming unbuilt products", () => {
    render(<InitiativesPage />);

    expect(
      screen.getByRole("link", { name: /haven — health-access navigation/i }),
    ).toHaveAttribute("href", "/initiatives/haven");
    expect(screen.getByText("Working demonstration")).toBeVisible();
    expect(screen.getByText("Planned")).toBeVisible();
    for (const forbidden of ["Harbor", "Beacon", "Labs"]) {
      expect(screen.queryByText(forbidden)).not.toBeInTheDocument();
    }
  });
});
