import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import BeaconPage, { metadata as beaconMetadata } from "./flagships/beacon/page";
import FhirPage, { metadata as fhirMetadata } from "./labs/interoperability/fhir-dashboard/page";
import ConverterPage, { metadata as converterMetadata } from "./labs/interoperability/hl7-fhir-converter/page";
import SimulatorPage, { metadata as simulatorMetadata } from "./labs/interoperability/ehr-workflow-simulator/page";
import { beaconConcept, interoperabilityConcepts } from "@/content/concepts";
import { flagshipModules } from "@/content/flagships";

const pages = [
  { name: "Beacon", Page: BeaconPage, metadata: beaconMetadata },
  { name: "FHIR Dashboard", Page: FhirPage, metadata: fhirMetadata },
  { name: "HL7-FHIR Converter", Page: ConverterPage, metadata: converterMetadata },
  { name: "EHR Workflow Simulator", Page: SimulatorPage, metadata: simulatorMetadata },
];

describe.each(pages)("$name concept scaffold", ({ name, Page, metadata }) => {
  it("has exact sections, honest placeholders, and one global safety footer", () => {
    render(<Page />);
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByRole("heading", { level: 1, name })).toBeVisible();
    for (const heading of [
      "Module purpose", "How it fits Zion", "Architecture summary", "Safety boundaries",
      "GitHub links placeholder", "Interview story placeholder", "Technical highlights placeholder",
    ]) {
      expect(screen.getByRole("heading", { level: 2, name: heading })).toBeVisible();
    }
    expect(screen.getByText("Concept / roadmap")).toHaveClass("status-badge--planned");
    expect(screen.getByText("Unimplemented; non-operational; synthetic-only.")).toBeVisible();
    expect(screen.getByText(/no implementation repository\/evidence link exists yet/i)).toBeVisible();
    expect(screen.getAllByText("Content will be added only after implementation and validation."))
      .toHaveLength(2);
    expect(screen.getAllByRole("contentinfo")).toHaveLength(1);
    expect(screen.getAllByRole("complementary", { name: "Global disclosure" })).toHaveLength(1);
    expect(metadata.title).toContain("Concept / roadmap");
    expect(metadata.description).toMatch(/unimplemented, non-operational.*synthetic-only/i);
  });

  it("makes no working demonstration, clinical, integration, or evidence claims", () => {
    const { container } = render(<Page />);
    const main = screen.getByRole("main");
    const safety = screen.getByRole("region", { name: "Safety boundaries" });
    expect(safety).toHaveTextContent(
      "No live clinical operation, real EHR connectivity, actual HL7/FHIR exchange, SMART on FHIR integration, standards conformance, certification, HIPAA compliance, diagnosis or treatment, production deployment, or existing GitHub implementation is claimed.",
    );
    expect(safety).toHaveTextContent("web scaffold checks are not implementation evidence");
    expect(safety).toHaveTextContent("Do not submit real PHI");
    expect(within(main).queryByRole("link")).not.toBeInTheDocument();
    expect(container.querySelector("form, input, textarea, select, button, iframe")).toBeNull();
    expect(container.querySelector(".status-badge--implemented")).toBeNull();
    expect(main.textContent).not.toMatch(
      /\bclinically (?:validated|proven)\b|\bproduction[- ]ready\b|\bHIPAA[- ]compliant\b|\b(?:connects to|exchanges with) (?:real|live) (?:EHR|FHIR)\b|\b(?:serving|used by) \d+ (?:patients|users)\b/i,
    );
    if (name === "Beacon") {
      expect(main).toHaveTextContent("Beacon has no runtime, API, client, models, migrations");
      expect(screen.getByRole("link", { name: "Flagships" })).toHaveAttribute("aria-current", "page");
    } else {
      expect(screen.getByRole("link", { name: "Interoperability Engineering" }))
        .toHaveAttribute("aria-current", "location");
    }
  });
});

it("keeps roadmap entries separate from the two implemented flagship records", () => {
  expect(flagshipModules.map((module) => module.id)).toEqual(["harbor", "haven"]);
  expect([beaconConcept, ...interoperabilityConcepts].map((concept) => concept.route)).toEqual([
    "/flagships/beacon",
    "/labs/interoperability/fhir-dashboard",
    "/labs/interoperability/hl7-fhir-converter",
    "/labs/interoperability/ehr-workflow-simulator",
  ]);
});
