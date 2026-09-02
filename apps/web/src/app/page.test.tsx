import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Home from "./page";

describe("Zion landing shell", () => {
  it("uses accessible page landmarks and a single primary heading", () => {
    render(<Home />);

    expect(screen.getByRole("banner")).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Primary" })).toBeInTheDocument();
    expect(screen.getByRole("main")).toHaveAttribute("id", "main-content");
    expect(screen.getByRole("contentinfo")).toBeInTheDocument();
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByRole("link", { name: "Skip to main content" })).toHaveAttribute(
      "href",
      "#main-content",
    );
  });

  it("links every primary page and marks Home as the current page", () => {
    render(<Home />);

    const nav = screen.getByRole("navigation", { name: "Primary" });
    for (const [label, href] of [
      ["Home", "/"],
      ["Initiatives", "/initiatives"],
      ["Projects", "/projects"],
      ["Evidence", "/evidence"],
    ]) {
      expect(screen.getByRole("link", { name: label })).toHaveAttribute("href", href);
    }
    expect(within(nav).getByRole("link", { name: "Home" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(within(nav).getByRole("link", { name: "Initiatives" })).not.toHaveAttribute(
      "aria-current",
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

  it("discloses the Zion categories and safety boundaries", () => {
    render(<Home />);

    expect(screen.getByRole("heading", { name: "Foundation status" })).toBeVisible();
    expect(screen.getByText(/no deployed service, real users, partners/i)).toBeVisible();
    expect(screen.getByText(/synthetic examples only/i)).toBeVisible();
    expect(screen.getByText(/does not provide diagnosis, medical advice/i)).toBeVisible();
    expect(screen.getByText(/three Zion avenues of impact/i)).toBeVisible();
    expect(screen.getByText(/care for the vulnerable/i)).toBeVisible();
    expect(screen.getByText(/healing & health access/i)).toBeVisible();
    expect(screen.getByText(/AI infrastructure, automation & empowerment/i)).toBeVisible();
    expect(screen.getByText(/not profit\. not surveillance\. not division\./i)).toBeVisible();
    expect(
      screen.getByText(/one line of code, one act of service, one community at a time/i),
    ).toBeVisible();
    for (const forbidden of ["Justin", "portfolio"]) {
      expect(screen.queryByText(forbidden)).not.toBeInTheDocument();
    }
  });
});
