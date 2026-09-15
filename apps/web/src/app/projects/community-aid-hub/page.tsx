import type { Metadata } from "next";
import { ProjectPage } from "@/components/ProjectPage";

export const metadata: Metadata = {
  title: "Community Aid Hub · Zion Software Initiative",
};

export default function CommunityAidHubPage() {
  return (
    <ProjectPage
      active="projects"
      eyebrow="Project area"
      slug="community-aid-hub"
      title="Community Aid Hub"
      status="implemented"
      intro="A synthetic coordination workspace for community aid. It shows how needs, matching, triage, and fulfillment can be tracked without exposing real people or claims."
      overview="The page keeps the cloud-and-castle direction honest: calm presentation, clear routes, and navy accents around a stable public-interest tool."
      purpose="Help coordinators move from a request to a plan with less confusion and fewer manual handoffs."
      audience={[
        "Community coordinators who need a truthful view of requests and capacity.",
        "Volunteers who need simple next steps and clear assignment boundaries.",
        "Engineers who need a bounded example of explainable matching and audit trails.",
      ]}
      features={[
        "Bounded request intake with explainable matching and rejection reasons.",
        "Capacity checks that stop unknown or stale inventory from being reserved.",
        "Approval-gated fulfillment with append-only audit records.",
      ]}
      limitations={[
        "No real recipients, dispatch, maps, or notification system.",
        "No claim of aid delivery, partner integrations, or field impact.",
        "Synthetic data only; no personal or location data is stored here.",
      ]}
      evidence={[
        {
          href: "/harbor",
          label: "Harbor case study",
          note: "The working demonstration that ties the coordination flow together.",
        },
        {
          href: "https://github.com/grey-ghost-1/zion-software-initiative/blob/main/apps/api/zion_api/routes/harbor.py",
          label: "apps/api/zion_api/routes/harbor.py",
          note: "Route logic for request review, matching, capacity, and fulfillment.",
        },
        {
          href: "https://github.com/grey-ghost-1/zion-software-initiative/blob/main/apps/web/src/app/harbor/HarborWorkflow.tsx",
          label: "apps/web/src/app/harbor/HarborWorkflow.tsx",
          note: "The accessible workflow UI for the Harbor experience.",
        },
        {
          href: "https://github.com/grey-ghost-1/zion-software-initiative/blob/main/apps/api/tests/test_harbor.py",
          label: "apps/api/tests/test_harbor.py",
          note: "Automated coverage for the coordination and safety rules.",
        },
      ]}
      relatedLinks={[
        { href: "/projects", label: "Back to projects index" },
        { href: "/projects/health-navigator", label: "Health Navigator" },
      ]}
    />
  );
}
