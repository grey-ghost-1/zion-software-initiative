import type { Metadata } from "next";
import { ConceptPage } from "@/components/ConceptPage";
import { interoperabilityConcepts } from "@/content/concepts";

export const metadata: Metadata = {
  title: "EHR Workflow Simulator Concept / roadmap · Zion Labs",
  description: "Unimplemented, non-operational workflow concept; synthetic-only web scaffold.",
};

export default function EhrWorkflowSimulatorPage() {
  return <ConceptPage concept={interoperabilityConcepts[2]} area="labs" />;
}
