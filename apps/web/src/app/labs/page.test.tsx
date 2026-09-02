import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import LabsPage from "./page";

describe("Labs page", () => {
  it("marks Labs as the current nav page and keeps one h1", () => {
    render(<LabsPage />);

    const nav = screen.getByRole("navigation", { name: "Primary" });
    expect(within(nav).getByRole("link", { name: "Labs" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });

  it("shows the audited prior-work snapshot and safe external links", () => {
    render(<LabsPage />);

    expect(
      screen.getByText(/Prior work by Justin Wimmer, originally published in the Batcomputer Portfolio/i),
    ).toBeVisible();
    expect(screen.getByText("23", { selector: "dd" })).toBeVisible();
    expect(screen.getByText("444", { selector: "dd" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Defensive security" })).toBeVisible();

    const externalLinks = screen
      .getAllByRole("link")
      .filter((link) => (link.getAttribute("href") ?? "").includes("github.com/grey-ghost-1/Batcomputer-Portfolio"));
    expect(externalLinks.length).toBeGreaterThan(0);
    for (const link of externalLinks) {
      expect(link).toHaveAttribute("target", "_blank");
      expect(link.getAttribute("rel")).toContain("noopener");
      expect(link.getAttribute("rel")).toContain("noreferrer");
    }
  });

  it("filters the grouped smaller labs without hiding the flagships", () => {
    render(<LabsPage />);

    fireEvent.click(screen.getByRole("button", { name: "IT support" }));

    expect(screen.getByText("Operations Platform")).toBeVisible();
    expect(screen.getByText("Orbital Data Lab")).toBeVisible();
    expect(screen.getByText("Algorithms & Quality")).toBeVisible();
    expect(screen.getByText("Alfred AI Assistant")).toBeVisible();
    expect(screen.getByRole("status")).toHaveTextContent("Showing 5 secondary labs");
    expect(screen.getByRole("heading", { name: "IT support", level: 3 })).toBeVisible();
    expect(screen.queryByRole("heading", { name: "Software automation", level: 3 })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Defensive security", level: 3 })).not.toBeInTheDocument();
  });
});
