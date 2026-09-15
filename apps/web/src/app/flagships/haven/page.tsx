import type { Metadata } from "next";
import { FlagshipPage } from "@/components/FlagshipPage";
import { getFlagshipModule } from "@/content/flagships";
import { HavenDemo } from "../../initiatives/haven/HavenDemo";

export const metadata: Metadata = {
  title: "Haven · Zion Software Initiative",
  description: "Haven's synthetic, non-diagnostic navigation demonstration.",
};

export default function HavenFlagshipPage() {
  const haven = getFlagshipModule("haven");

  return (
    <FlagshipPage
      module={haven}
      safetyNotice={
        <section aria-label="Emergency help" role="region" className="status-section">
          <h2>If you need help right now</h2>
          <p>
            If anyone is in immediate physical danger, <strong>call 911</strong> (United
            States). If you may hurt yourself or someone else,{" "}
            <strong>call or text 988</strong> or visit{" "}
            <a href="https://988lifeline.org/">988lifeline.org</a>. This demonstration
            does not monitor you or contact anyone on your behalf.
          </p>
        </section>
      }
      demo={<HavenDemo />}
    />
  );
}
