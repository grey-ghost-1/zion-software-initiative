import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Home from "./page";

describe("unified Zion homepage", () => {
  it("uses the shared accessible shell and exact primary navigation", () => {
    render(<Home />);

    expect(screen.getByRole("banner")).toBeInTheDocument();
    expect(screen.getByRole("main")).toHaveAttribute("id", "main-content");
    expect(screen.getByRole("contentinfo")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Skip to main content" })).toHaveAttribute(
      "href",
      "#main-content",
    );
    const nav = screen.getByRole("navigation", { name: "Primary" });
    expect(within(nav).getAllByRole("link").map((link) => link.textContent)).toEqual([
      "Mission",
      "Architecture",
      "Flagships",
      "Zion Labs",
    ]);
    for (const [label, href] of [
      ["Mission", "/mission"],
      ["Architecture", "/architecture"],
      ["Flagships", "/flagships"],
      ["Zion Labs", "/labs"],
    ]) {
      expect(within(nav).getByRole("link", { name: label })).toHaveAttribute("href", href);
    }
    expect(within(nav).queryByRole("link", { current: "page" })).toBeNull();
    expect(screen.getByRole("link", { name: "Zion home" })).toHaveAttribute("href", "/");
    expect(screen.getByRole("link", { name: "View source" })).toHaveAttribute(
      "href",
      "https://github.com/grey-ghost-1/zion-software-initiative",
    );
  });

  it("discloses status globally and links exactly two canonical flagships", () => {
    render(<Home />);

    const disclosure = screen.getByRole("complementary", { name: "Global disclosure" });
    expect(disclosure).toHaveTextContent(
      "This platform uses synthetic data, does not diagnose or treat, does not collect real health information, and is not an operational public service.",
    );
    expect(disclosure).toHaveTextContent("no hosted production deployment");
    const flagshipNav = screen.getByRole("navigation", { name: "Flagship pages" });
    expect(within(flagshipNav).getByRole("link", { name: "Explore Harbor" })).toHaveAttribute(
      "href",
      "/flagships/harbor",
    );
    expect(within(flagshipNav).getByRole("link", { name: "Explore Haven" })).toHaveAttribute(
      "href",
      "/flagships/haven",
    );
  });
});
