import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import LabsPage from "./page";

describe("Zion Labs index", () => {
  it("separates concepts and prior work from implemented flagships", () => {
    render(<LabsPage />);

    expect(screen.getByRole("link", { name: "Zion Labs" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("link", { name: "Read the concept roadmap" })).toHaveAttribute(
      "href",
      "/labs/interoperability",
    );
    expect(screen.getByRole("link", { name: "Review prior-work evidence" })).toHaveAttribute(
      "href",
      "/labs/prior-work",
    );
    expect(screen.getByText(/listing here is not a Zion capability/i)).toBeVisible();
  });
});
