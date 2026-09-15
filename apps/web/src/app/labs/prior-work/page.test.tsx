import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import archive from "../../../../../../docs/evidence/zion-labs-prior-work.json";
import PriorWorkPage from "./page";

describe("Zion Labs prior work", () => {
  it("provides required attribution and immutable audited links without copied material", () => {
    render(<PriorWorkPage />);

    expect(screen.getByText(/originally published in the Batcomputer Portfolio/i).closest("p"))
      .toHaveTextContent("Creator: Justin Wimmer");
    expect(screen.getByText(/originally published in the Batcomputer Portfolio/i)).toBeVisible();
    expect(screen.getByText(/no reuse license was identified/i)).toBeVisible();
    expect(screen.getByText(/reproduces no Batcomputer branding, source code, project copy, or assets/i)).toBeVisible();
    expect(screen.getByText(archive.sourceSnapshot.commit)).toBeVisible();
    const inventory = screen.getByRole("heading", { name: "Evidence links" }).closest("section")!;
    expect(within(inventory).getAllByRole("listitem")).toHaveLength(archive.projects.length);
    for (const project of archive.projects) {
      expect(screen.getByRole("link", { name: project.name })).toHaveAttribute(
        "href",
        project.source.immutableUrl,
      );
      expect(project.source.immutableUrl).toContain(archive.sourceSnapshot.commit);
    }
  });
});
