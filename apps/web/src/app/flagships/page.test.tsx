import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import FlagshipsPage from "./page";

describe("flagships page", () => {
  it("renders the two catalog modules and their existing routes", () => {
    const { container } = render(<FlagshipsPage />);

    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByRole("heading", { name: "Harbor" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Haven" })).toBeVisible();
    expect(screen.getByRole("link", { name: "Open the existing Harbor route" })).toHaveAttribute(
      "href",
      "/harbor",
    );
    expect(screen.getByRole("link", { name: "Open the existing Haven route" })).toHaveAttribute(
      "href",
      "/initiatives/haven",
    );

    const excludedModuleName = ["Bea", "con"].join("");
    expect(container).not.toHaveTextContent(excludedModuleName);
  });

  it("shows truthful module status, boundaries, evidence, and interview structure", () => {
    render(<FlagshipsPage />);

    expect(screen.getAllByText("Implemented synthetic demonstration")).toHaveLength(2);
    expect(screen.getAllByText("Not deployed or production-verified")).toHaveLength(2);
    for (const heading of [
      "Purpose",
      "How it fits Zion",
      "Actual architecture",
      "Boundaries and limitations",
      "Interview story",
      "Evidence",
    ]) {
      expect(screen.getAllByRole("heading", { name: heading })).toHaveLength(2);
    }
  });
});
