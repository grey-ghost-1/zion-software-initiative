import type { Metadata } from "next";
import { ProjectPage } from "@/components/ProjectPage";

export const metadata: Metadata = {
  title: "Health Navigator · Zion Software Initiative",
};

export default function HealthNavigatorPage() {
  return (
    <ProjectPage
      active="projects"
      eyebrow="Project area"
      slug="health-navigator"
      title="Health Navigator"
      status="implemented"
      intro="A synthetic health-access navigator that stays out of diagnosis and focuses on plain-language next steps, crisis routing, and curated references."
      overview="The page keeps the cloud theme soft and readable while using navy accents to make the safety boundary feel deliberate rather than decorative."
      purpose="Help a visitor understand where to start when they are confused, without pretending to be a clinician."
      audience={[
        "People who need a clear first step and plain-language routing.",
        "Care navigators who want a non-diagnostic example of safe guidance.",
        "Engineers who want a bounded crisis-first flow with explicit limits.",
      ]}
      features={[
        "Emergency and crisis inputs short-circuit to 911/988 guidance.",
        "Explanation cards preserve the meaning of the original concern in plain language.",
        "Curated references point only to official or educational health resources.",
      ]}
      limitations={[
        "No diagnosis, treatment, medication, dose, or prognosis.",
        "No medical records, personal histories, or live monitoring.",
        "No claim of clinical review, HIPAA compliance, or provider partnership.",
      ]}
      evidence={[
        {
          href: "/initiatives/haven",
          label: "Haven case study",
          note: "The public demonstration that shows the health-access flow.",
        },
        {
          href: "https://github.com/grey-ghost-1/zion-software-initiative/blob/main/apps/web/src/app/initiatives/haven/page.tsx",
          label: "apps/web/src/app/initiatives/haven/page.tsx",
          note: "The main page for the navigation experience and boundary disclosures.",
        },
        {
          href: "https://github.com/grey-ghost-1/zion-software-initiative/blob/main/apps/web/src/app/initiatives/haven/HavenDemo.tsx",
          label: "apps/web/src/app/initiatives/haven/HavenDemo.tsx",
          note: "The synthetic concern-to-routing demonstration widget.",
        },
        {
          href: "https://github.com/grey-ghost-1/zion-software-initiative/blob/main/apps/api/zion_api/routes/haven.py",
          label: "apps/api/zion_api/routes/haven.py",
          note: "The API route that serves the Haven data and review flow.",
        },
      ]}
      relatedLinks={[
        { href: "/projects", label: "Back to projects index" },
        { href: "/projects/community-aid-hub", label: "Community Aid Hub" },
      ]}
    />
  );
}
