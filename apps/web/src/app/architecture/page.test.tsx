import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ArchitecturePage from "./page";

describe("architecture page", () => {
  it("provides accessible landmarks and a semantic diagram equivalent", () => {
    render(<ArchitecturePage />);

    expect(screen.getByRole("main")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Architecture" })).toHaveAttribute(
      "aria-current",
      "page",
    );
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
    expect(screen.getByText(/managed production PostgreSQL, public HTTPS verification/i)).toBeVisible();
    expect(screen.getByText(/rollback exercise remain pending or unverified/i)).toBeVisible();
    const readiness = screen.getByRole("region", { name: "Implemented checks are not a production claim" });
    for (const name of ["CI/CD", "Health", "Logging", "Rollback"]) {
      const section = within(readiness).getByRole("heading", { name }).closest("article")!;
      expect(section).toHaveTextContent("Production evidence placeholder");
      expect(section).toHaveTextContent(/validation/i);
    }
  });

  it("keeps implemented modules separate from non-operational concept scaffolds", () => {
    render(<ArchitecturePage />);
    const catalog = screen.getByRole("region", { name: "Platform catalog and implementation status" });
    expect(within(catalog).getAllByText("Implemented synthetic demonstration")).toHaveLength(2);
    expect(within(catalog).getAllByText("Concept / roadmap")).toHaveLength(2);
    for (const [name, route] of [
      ["Harbor", "/flagships/harbor"],
      ["Haven", "/flagships/haven"],
      ["Beacon governance/workflow concept", "/flagships/beacon"],
      ["FHIR Dashboard", "/labs/interoperability/fhir-dashboard"],
      ["HL7-FHIR Converter", "/labs/interoperability/hl7-fhir-converter"],
      ["EHR Workflow Simulator", "/labs/interoperability/ehr-workflow-simulator"],
    ]) {
      expect(within(catalog).getByRole("link", { name })).toHaveAttribute("href", route);
    }
    expect(catalog).toHaveTextContent("not a restored runtime or a third implemented flagship");
    expect(screen.getByText(/they are design requirements, not implemented protections/i)).toBeVisible();
  });
});
