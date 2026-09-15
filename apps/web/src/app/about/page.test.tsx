import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AboutPage from "./page";

describe("About Justin page", () => {
  it("marks About Justin as the current nav page and keeps one h1", () => {
    render(<AboutPage />);

    const nav = screen.getByRole("navigation", { name: "Primary" });
    expect(within(nav).getByRole("link", { name: "About Justin" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });

  it("links to GitHub for verification and contact, with no registration or contact form", () => {
    render(<AboutPage />);

    expect(screen.getByRole("link", { name: "View my GitHub profile" })).toHaveAttribute(
      "href",
      "https://github.com/grey-ghost-1",
    );
    expect(screen.queryByRole("textbox")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /sign up|register/i })).not.toBeInTheDocument();
  });
});
