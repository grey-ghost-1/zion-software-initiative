import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import InteroperabilityRoadmapPage from "./page";

describe("interoperability roadmap", () => {
  it("labels every item as an unimplemented concept", () => {
    render(<InteroperabilityRoadmapPage />);

    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByText("Concept / roadmap")).toBeVisible();
    expect(screen.getByText(/zero functional implementation or runtime tests/i)).toBeVisible();
    for (const [name, slug] of [
      ["FHIR Dashboard", "fhir-dashboard"],
      ["HL7-FHIR Converter", "hl7-fhir-converter"],
      ["EHR Workflow Simulator", "ehr-workflow-simulator"],
    ]) {
      expect(screen.getByRole("heading", { name })).toBeVisible();
      expect(screen.getByRole("link", { name: `Read the ${name} concept` })).toHaveAttribute(
        "href", `/labs/interoperability/${slug}`,
      );
    }
    expect(screen.getAllByText(/only a static concept route and web scaffold checks exist/i)).toHaveLength(3);
    for (const name of [
      "Module purpose", "How it fits Zion", "Architecture summary", "Safety boundaries",
      "GitHub links placeholder", "Interview story placeholder", "Technical highlights placeholder",
    ]) {
      expect(screen.getByRole("heading", { name })).toBeVisible();
    }
  });

  it("rejects operational, clinical, compliance, and deployment claims", () => {
    render(<InteroperabilityRoadmapPage />);

    expect(
      screen.getByText(/no real EHR connectivity, HL7 or FHIR exchange/i),
    ).toBeVisible();
    expect(screen.getByText(/standards conformance, certification, clinical use/i)).toBeVisible();
    expect(screen.getByText(/HIPAA compliance, real PHI, diagnosis or treatment/i)).toBeVisible();
    expect(screen.getByText(/no functional implementation, runtime tests, external demo, or prior-work claim/i)).toBeVisible();
    expect(screen.getByText(/no Batcomputer content or assets are copied/i)).toBeVisible();
  });
});
