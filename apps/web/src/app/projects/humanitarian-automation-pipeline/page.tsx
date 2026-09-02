import type { Metadata } from "next";
import { ProjectPage } from "@/components/ProjectPage";

export const metadata: Metadata = {
  title: "Humanitarian Automation Pipeline · Zion Software Initiative",
};

export default function HumanitarianAutomationPipelinePage() {
  return (
    <ProjectPage
      active="projects"
      eyebrow="Project area"
      slug="humanitarian-automation-pipeline"
      title="Humanitarian Automation Pipeline"
      status="implemented"
      intro="A synthetic automation pipeline for coordination and empowerment. It turns a fixed fixture into a typed workflow, explainable allocation proposal, and required human decision."
      overview="The page keeps the castle metaphor quiet and the cloud theme calm: the system is built to be inspectable, not theatrical."
      purpose="Show how automation can reduce repetitive coordination work while still keeping people in control of the outcome."
      audience={[
        "Nonprofits and coordinators who need structured, reviewable workflows.",
        "People learning how policy, provenance, and human approval fit together.",
        "Engineers who want a deterministic example of safe workflow automation.",
      ]}
      features={[
        "Typed workflow steps with explicit success, retry, timeout, and replay states.",
        "Explainable allocation output with reasons, totals, and remaining inventory.",
        "Policy, provenance, and approval checks before the run can complete.",
      ]}
      limitations={[
        "No real disasters, dispatch, purchasing, or public-warning output.",
        "No autonomous action without a human decision.",
        "Synthetic fixture data only; no claim of operational deployment.",
      ]}
      evidence={[
        {
          href: "/initiatives/beacon",
          label: "Beacon case study",
          note: "The public demonstration page for the pipeline.",
        },
        {
          href: "https://github.com/grey-ghost-1/zion-software-initiative/blob/main/apps/web/src/app/initiatives/beacon/page.tsx",
          label: "apps/web/src/app/initiatives/beacon/page.tsx",
          note: "The public page that explains the synthetic pipeline and disclosures.",
        },
        {
          href: "https://github.com/grey-ghost-1/zion-software-initiative/blob/main/apps/api/zion_api/services/beacon/engine.py",
          label: "apps/api/zion_api/services/beacon/engine.py",
          note: "The deterministic state machine that drives the workflow.",
        },
        {
          href: "https://github.com/grey-ghost-1/zion-software-initiative/blob/main/apps/api/tests/test_beacon_allocation.py",
          label: "apps/api/tests/test_beacon_allocation.py",
          note: "Automated coverage for the allocation rules and reasons.",
        },
      ]}
      relatedLinks={[
        { href: "/projects", label: "Back to projects index" },
        { href: "/projects/community-aid-hub", label: "Community Aid Hub" },
        { href: "/projects/health-navigator", label: "Health Navigator" },
      ]}
    />
  );
}
