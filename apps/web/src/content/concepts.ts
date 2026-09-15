export type ConceptModule = {
  id: string;
  name: string;
  route: string;
  purpose: string;
  fit: string;
  architecture: string;
};

export const beaconConcept = {
  id: "beacon",
  name: "Beacon",
  route: "/flagships/beacon",
  purpose:
    "Explore a possible governance and human-review workflow for fabricated coordination scenarios. This is a roadmap question, not a working module.",
  fit:
    "Beacon would study approval boundaries and decision provenance on Zion's governed foundation. Harbor and Haven remain the only implemented flagship demonstrations.",
  architecture:
    "Proposed direction only: synthetic scenario definitions, explicit review states, and human approval records. This page is static web scaffolding; Beacon has no runtime, API, client, models, migrations, or operational workflow.",
} as const satisfies ConceptModule;

export const interoperabilityConcepts = [
  {
    id: "fhir-dashboard",
    name: "FHIR Dashboard",
    route: "/labs/interoperability/fhir-dashboard",
    purpose:
      "Could a future synthetic-data interface make standards-shaped resource relationships understandable without implying clinical authority?",
    fit:
      "This Labs concept would explore transparent presentation and provenance using fabricated examples, separate from Zion's implemented Harbor and Haven modules.",
    architecture:
      "Proposed direction only: local fabricated resource fixtures and a read-only relationship view. No FHIR server, resource processing, exchange, or conformance validation is implemented.",
  },
  {
    id: "hl7-fhir-converter",
    name: "HL7-FHIR Converter",
    route: "/labs/interoperability/hl7-fhir-converter",
    purpose:
      "Could a future offline teaching tool explain mapping tradeoffs using fabricated examples and explicit validation failures?",
    fit:
      "This Labs concept would explore explainable mapping decisions and safety boundaries, not add an exchange capability to Zion.",
    architecture:
      "Proposed direction only: fabricated message examples, an offline mapping exercise, and a human-readable explanation of rejected mappings. No parser, converter, HL7/FHIR exchange, or standards-conformance validation is implemented.",
  },
  {
    id: "ehr-workflow-simulator",
    name: "EHR Workflow Simulator",
    route: "/labs/interoperability/ehr-workflow-simulator",
    purpose:
      "Could a future simulator help engineers study human review points without connecting to a real care environment?",
    fit:
      "This Labs concept would explore explicit approval states and transparent decisions with synthetic scenarios, not extend Haven into clinical operation.",
    architecture:
      "Proposed direction only: a local, fabricated workflow state model with simulated review checkpoints. No simulator, EHR connection, clinical automation, or patient-record processing is implemented.",
  },
] as const satisfies readonly ConceptModule[];
