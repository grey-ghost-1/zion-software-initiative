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

  it("distinguishes the implemented Harbor prototype from unbuilt directions", () => {
    render(<InitiativesPage />);

    expect(
      screen.getByText(/one synthetic, inspectable prototype/i),
    ).toBeVisible();
    expect(screen.getByText("Synthetic prototype")).toBeVisible();
    expect(
      screen.getAllByRole("link", { name: "Harbor" }).some(
        (link) => link.getAttribute("href") === "/harbor",
      ),
    ).toBe(true);
    expect(screen.getByText(/Haven and Beacon remain unimplemented/i)).toBeVisible();
  });
});
