import type { Metadata } from "next";
import { ConceptPage } from "@/components/ConceptPage";
import { interoperabilityConcepts } from "@/content/concepts";

export const metadata: Metadata = {
  title: "FHIR Dashboard Concept / roadmap · Zion Labs",
  description: "Unimplemented, non-operational dashboard concept; synthetic-only web scaffold.",
};

export default function FhirDashboardPage() {
  return <ConceptPage concept={interoperabilityConcepts[0]} area="labs" />;
}
