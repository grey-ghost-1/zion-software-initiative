export type FlagshipStatus = {
  implementation: "implemented";
  label: string;
  operational: "not-operational";
  operationalLabel: string;
};

export type EvidenceLink = {
  label: string;
  href: string;
};

export type InterviewStory = {
  problem: string;
  constraints: string;
  architecture: string;
  safety: string;
  outcome: string;
};

export type FlagshipModule = {
  id: "harbor" | "haven";
  name: string;
  descriptor: string;
  route: "/harbor" | "/initiatives/haven";
  purpose: string;
  fit: string;
  architecture: string;
  boundaries: readonly string[];
  status: FlagshipStatus;
  evidence: readonly EvidenceLink[];
  interviewStory: InterviewStory;
};

const REPOSITORY_BASE =
  "https://github.com/grey-ghost-1/zion-software-initiative/blob/main";

export const flagshipModules = [
  {
    id: "harbor",
    name: "Harbor",
    descriptor: "Community coordination",
    route: "/harbor",
    purpose:
      "Demonstrate an understandable, human-approved workflow for coordinating synthetic assistance requests, constrained resources, volunteer plans, and fulfillment.",
    fit:
      "Harbor is Zion's community-coordination module. It applies the platform's shared access controls, explainability, auditability, and human-approval model to non-emergency aid workflows.",
    architecture:
      "A Next.js workflow uses the typed Zion API client to call organization-scoped FastAPI routes. The modular-monolith service applies deterministic matching and capacity rules, then persists synthetic workflow and append-only audit records through SQLAlchemy in PostgreSQL.",
    boundaries: [
      "Synthetic requests, organizations, capacity, and volunteer records only; no real vulnerable-person data.",
      "Not an emergency-response, dispatch, shelter-booking, case-management, or aid-delivery service.",
      "No autonomous allocation: a coordinator must review and approve sensitive workflow changes.",
      "No deployed service, real users, partners, live capacity feed, maps, notifications, or measured field outcomes.",
    ],
    status: {
      implementation: "implemented",
      label: "Implemented synthetic demonstration",
      operational: "not-operational",
      operationalLabel: "Not deployed or production-verified",
    },
    evidence: [
      { label: "Open the Harbor demonstration", href: "/harbor" },
      {
        label: "Inspect the Harbor API routes",
        href: `${REPOSITORY_BASE}/apps/api/zion_api/routes/harbor.py`,
      },
      {
        label: "Inspect the typed API client",
        href: `${REPOSITORY_BASE}/packages/api-client/src/index.ts`,
      },
    ],
    interviewStory: {
      problem:
        "Community coordinators need to compare requests, resource fit, capacity, and volunteer availability without hiding tradeoffs behind an opaque score.",
      constraints:
        "The public demonstration cannot use personal data, imply live capacity, overbook constrained resources, or let software make sensitive allocations on its own.",
      architecture:
        "The UI and typed client call organization-scoped FastAPI endpoints; deterministic services return score components and rejection reasons; PostgreSQL constraints protect capacity and preserve workflow history.",
      safety:
        "Coarse synthetic data, server-side RBAC, organization isolation, stale-capacity handling, explicit coordinator approval, and append-only audit events bound every action.",
      outcome:
        "The implemented slice makes a proposed match inspectable from request through approval and fulfillment while remaining a non-operational engineering demonstration.",
    },
  },
  {
    id: "haven",
    name: "Haven",
    descriptor: "Non-diagnostic navigation",
    route: "/initiatives/haven",
    purpose:
      "Demonstrate plain-language, non-diagnostic navigation from a synthetic concern to bounded next steps and curated official resources.",
    fit:
      "Haven is Zion's health-access navigation module. It shows how the same responsible-engineering foundation can clarify choices while refusing diagnosis, treatment, prediction, and autonomous clinical action.",
    architecture:
      "A Next.js interface and typed API client connect to a FastAPI module with deterministic emergency and crisis routing, content-preservation validation, organization-scoped review, SQLAlchemy models, and PostgreSQL-backed audit records. Visitor scenarios remain synthetic and ephemeral.",
    boundaries: [
      "Synthetic, ephemeral scenarios only; no real patients, medical records, free-form symptom histories, or real PHI.",
      "No diagnosis, treatment, medication, dose, prognosis, risk percentage, or medical advice.",
      "No monitoring, clinical decision-making, contacting services, healthcare-provider affiliation, or real EHR integration.",
      "No claim of HIPAA compliance, clinical review, production deployment, or measured health outcomes.",
    ],
    status: {
      implementation: "implemented",
      label: "Implemented synthetic demonstration",
      operational: "not-operational",
      operationalLabel: "Not deployed or production-verified",
    },
    evidence: [
      { label: "Open the Haven demonstration", href: "/initiatives/haven" },
      {
        label: "Inspect the Haven API routes",
        href: `${REPOSITORY_BASE}/apps/api/zion_api/routes/haven.py`,
      },
      {
        label: "Inspect deterministic routing",
        href: `${REPOSITORY_BASE}/apps/api/zion_api/services/haven_routing.py`,
      },
    ],
    interviewStory: {
      problem:
        "People can struggle to understand where to start when care instructions, costs, and service categories are unfamiliar.",
      constraints:
        "The demonstration must offer useful orientation without collecting patient data, diagnosing, recommending treatment, or weakening fixed emergency and crisis guidance.",
      architecture:
        "The UI presents ephemeral synthetic scenarios; deterministic routing runs before optional storage; validation preserves critical source facts; organization-scoped review and audit endpoints sit behind the typed client.",
      safety:
        "Fixed emergency and crisis routes bypass database dependencies, prohibited clinical outputs are rejected, resources are curated, and reviewer actions require RBAC and organization isolation.",
      outcome:
        "The implemented slice demonstrates explainable navigation and review while clearly remaining non-clinical, non-operational, and unsuitable for real patient use.",
    },
  },
] as const satisfies readonly FlagshipModule[];

export function getFlagshipModule(id: FlagshipModule["id"]): FlagshipModule {
  const flagship = flagshipModules.find((candidate) => candidate.id === id);
  if (!flagship) {
    throw new Error(`Unknown flagship module: ${id}`);
  }
  return flagship;
}
