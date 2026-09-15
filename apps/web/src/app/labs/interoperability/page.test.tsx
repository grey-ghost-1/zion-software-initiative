import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import InteroperabilityRoadmapPage from "./page";

describe("interoperability roadmap", () => {
  it("labels every item as an unimplemented concept", () => {
    render(<InteroperabilityRoadmapPage />);

    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByText("Unimplemented concepts")).toBeVisible();
    expect(screen.getByText(/zero implementation and zero tests/i)).toBeVisible();
    for (const name of [
      "FHIR Dashboard",
      "HL7-to-FHIR Converter",
      "EHR Workflow Simulator",
    ]) {
      expect(screen.getByRole("heading", { name })).toBeVisible();
    }
    expect(screen.getAllByText(/not started; no code, tests, route/i)).toHaveLength(3);
  });

  it("rejects operational, clinical, compliance, and deployment claims", () => {
    render(<InteroperabilityRoadmapPage />);

    expect(
      screen.getByText(/no real EHR connectivity, HL7 or FHIR exchange/i),
    ).toBeVisible();
    expect(screen.getByText(/SMART on FHIR integration/i)).toBeVisible();
    expect(screen.getByText(/standards conformance, certification, clinical use/i)).toBeVisible();
    expect(screen.getByText(/HIPAA compliance, real PHI, diagnosis or treatment/i)).toBeVisible();
    expect(screen.getByText(/no Batcomputer content or assets are copied/i)).toBeVisible();
  });
});
