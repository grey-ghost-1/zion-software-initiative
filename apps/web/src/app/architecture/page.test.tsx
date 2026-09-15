import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ArchitecturePage from "./page";

describe("architecture page", () => {
  it("provides accessible landmarks and a semantic diagram equivalent", () => {
    render(<ArchitecturePage />);

    expect(screen.getByRole("main")).toBeInTheDocument();
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(
      screen.getByText(/requests move from the Next\.js user interface/i),
    ).toBeInTheDocument();

    const table = screen.getByRole("table", {
      name: "Semantic text equivalent of the platform diagram",
    });
    for (const layer of [
      "Next.js UI",
      "Typed API client",
      "FastAPI modular monolith",
      "PostgreSQL",
      "Cross-cutting layers",
    ]) {
      expect(within(table).getByRole("rowheader", { name: layer })).toBeVisible();
    }
  });

  it("states every shared safety principle", () => {
    render(<ArchitecturePage />);

    for (const principle of [
      "Synthetic data only",
      "Deterministic safety rules",
      "Transparent decisions",
      "Provenance",
      "RBAC and organization isolation",
      "Audit trails",
      "No diagnosis or treatment",
      "No autonomous dispatch",
      "No real PHI",
      "Human approval for sensitive actions",
    ]) {
      expect(screen.getByText(principle)).toBeVisible();
    }
  });

  it("separates implemented checks from pending production work", () => {
    render(<ArchitecturePage />);

    expect(screen.getByText(/Automated CI runs lint, type, test, and build checks/i)).toBeVisible();
    expect(screen.getByText(/health and readiness endpoints are implemented/i)).toBeVisible();
    expect(screen.getByText(/managed PostgreSQL, HTTPS termination/i)).toBeVisible();
    expect(screen.getByText(/rollback verification remain pending/i)).toBeVisible();
  });
});
