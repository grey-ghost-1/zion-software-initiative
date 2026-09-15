import type { Metadata } from "next";
import { ConceptPage } from "@/components/ConceptPage";
import { beaconConcept } from "@/content/concepts";

export const metadata: Metadata = {
  title: "Beacon Concept / roadmap · Zion",
  description: "Unimplemented, non-operational governance concept; synthetic-only web scaffold.",
};

export default function BeaconConceptPage() {
  return <ConceptPage concept={beaconConcept} area="flagships" />;
}
