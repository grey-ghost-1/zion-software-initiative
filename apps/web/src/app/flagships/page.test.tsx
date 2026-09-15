import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import FlagshipsPage from "./page";

describe("flagships page", () => {
  it("renders the two catalog modules and their canonical routes", () => {
    const { container } = render(<FlagshipsPage />);

    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByRole("link", { name: "Flagships" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("heading", { name: "Harbor" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Haven" })).toBeVisible();
    expect(screen.getByRole("link", { name: "Open Harbor" })).toHaveAttribute(
      "href",
      "/flagships/harbor",
    );
    expect(screen.getByRole("link", { name: "Open Haven" })).toHaveAttribute(
      "href",
      "/flagships/haven",
    );

    const excludedModuleName = ["Bea", "con"].join("");
    expect(container).not.toHaveTextContent(excludedModuleName);
  });

  it("shows truthful module status, boundaries, evidence, and interview structure", () => {
    render(<FlagshipsPage />);

    expect(screen.getAllByText("Implemented synthetic demonstration")).toHaveLength(2);
    expect(screen.getAllByText("Not deployed or production-verified")).toHaveLength(2);
    for (const heading of [
      "Module Purpose",
      "How it fits Zion",
      "Architecture Summary",
      "Boundaries and Limitations",
      "Interview Story",
      "Demo and Evidence",
    ]) {
      expect(screen.getAllByRole("heading", { name: heading })).toHaveLength(2);
    }
  });
});
