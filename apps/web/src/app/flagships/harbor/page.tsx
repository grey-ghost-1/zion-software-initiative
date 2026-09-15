import type { Metadata } from "next";
import { FlagshipPage } from "@/components/FlagshipPage";
import { getFlagshipModule } from "@/content/flagships";
import { HarborWorkflow } from "../../harbor/HarborWorkflow";

export const metadata: Metadata = {
  title: "Harbor · Zion Software Initiative",
  description: "Harbor's synthetic, human-approved community coordination demonstration.",
};

export default function HarborFlagshipPage() {
  const harbor = getFlagshipModule("harbor");

  return (
    <FlagshipPage
      module={harbor}
      safetyNotice={
        <aside className="status-section" aria-labelledby="harbor-control-title">
          <h2 id="harbor-control-title">Capacity and approval controls</h2>
          <p>
            Unknown or stale capacity is unavailable. Harbor cannot reserve capacity until
            a coordinator explicitly reviews and approves a proposal; database constraints
            and an atomic conditional update prevent overbooking.
          </p>
        </aside>
      }
      demo={<HarborWorkflow />}
    />
  );
}
