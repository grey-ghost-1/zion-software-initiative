import type { Metadata } from "next";
import { ConceptPage } from "@/components/ConceptPage";
import { interoperabilityConcepts } from "@/content/concepts";

export const metadata: Metadata = {
  title: "HL7-FHIR Converter Concept / roadmap · Zion Labs",
  description: "Unimplemented, non-operational mapping concept; synthetic-only web scaffold.",
};

export default function Hl7FhirConverterPage() {
  return <ConceptPage concept={interoperabilityConcepts[1]} area="labs" />;
}
