import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Home from "./page";

describe("Zion landing shell", () => {
  it("uses accessible page landmarks and a single primary heading", () => {
    render(<Home />);

    expect(screen.getByRole("banner")).toBeInTheDocument();
    expect(screen.getByRole("main")).toHaveAttribute("id", "main-content");
    expect(screen.getByRole("contentinfo")).toBeInTheDocument();
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByRole("link", { name: "Skip to main content" })).toHaveAttribute(
      "href",
      "#main-content",
    );
  });

  it("links to source and project boundaries without implying a live demo", () => {
    render(<Home />);

    expect(screen.getByRole("link", { name: "View source" })).toHaveAttribute(
      "href",
      "https://github.com/grey-ghost-1/zion-software-initiative",
    );
    expect(
      screen.getByRole("link", { name: "Read the project boundaries" }),
    ).toHaveAttribute(
      "href",
      "https://github.com/grey-ghost-1/zion-software-initiative/blob/main/README.md",
    );
    expect(screen.queryByRole("link", { name: /demo/i })).not.toBeInTheDocument();
  });

  it("discloses foundation status and safety boundaries", () => {
    render(<Home />);

    expect(screen.getByRole("heading", { name: "Foundation status" })).toBeVisible();
    expect(screen.getByText(/no live workflows, real users, partnerships/i)).toBeVisible();
    expect(screen.getByText(/synthetic examples and curated public data only/i)).toBeVisible();
    expect(screen.getByText(/does not provide diagnosis, medical advice/i)).toBeVisible();
  });
});
