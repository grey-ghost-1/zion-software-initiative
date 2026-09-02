export type SecondaryLabCategory =
  | "software/automation"
  | "defensive security"
  | "IT support"
  | "networking/systems";

export type FlagshipLabCategory = "platform" | "simulation" | "algorithms" | "assistant";

export type LabCategory = SecondaryLabCategory | FlagshipLabCategory;
export type LabTier = "flagship" | "secondary";

export interface LabProjectValidation {
  status: string;
  notes: string;
}

export interface LabProjectSource {
  path: string;
  immutableUrl: string;
}

export interface LabProject {
  id: string;
  name: string;
  slug: string;
  tier: LabTier;
  category: LabCategory;
  relationship: string;
  summary: string;
  features: string[];
  limitations: string[];
  source: LabProjectSource;
  evidenceUrls: string[];
  validation: LabProjectValidation;
  media: string[];
  copyAssets: false;
}

export interface LabsArchiveSnapshot {
  projectCount: number;
  flagshipCount: number;
  secondaryCount: number;
  secondaryByCategory: Record<SecondaryLabCategory, number>;
  retainedLegacyFolders: number;
  ciTotals: Array<{ label: string; tests: number }>;
  passingTotal: number;
}

export interface LabsArchive {
  schemaVersion: number;
  attribution: {
    creator: string;
    origin: string;
    reuseLicense: null;
  };
  sourceSnapshot: {
    repo: string;
    defaultBranch: string;
    commit: string;
    auditedAt: string;
    inventoryUrl: string;
    ciRunUrl: string;
  };
  validationSnapshot: LabsArchiveSnapshot;
  projects: LabProject[];
  media: [];
  copyAssets: false;
}

export const SECONDARY_CATEGORY_ORDER: SecondaryLabCategory[] = [
  "software/automation",
  "defensive security",
  "IT support",
  "networking/systems",
];

export function getFeaturedLabs(archive: LabsArchive): LabProject[] {
  return archive.projects.filter((project) => project.tier === "flagship");
}

export function getSecondaryLabs(archive: LabsArchive): LabProject[] {
  return archive.projects.filter((project) => project.tier === "secondary");
}

export function getSecondaryLabsByCategory(
  archive: LabsArchive,
  category: SecondaryLabCategory | "all",
): Array<{ category: SecondaryLabCategory; projects: LabProject[] }> {
  const secondaryLabs = getSecondaryLabs(archive);
  const categories =
    category === "all" ? SECONDARY_CATEGORY_ORDER : SECONDARY_CATEGORY_ORDER.filter((item) => item === category);

  return categories
    .map((item) => ({
      category: item,
      projects: secondaryLabs.filter((project) => project.category === item),
    }))
    .filter((group) => group.projects.length > 0);
}

export function formatValidationStatus(status: string): string {
  return status.replace(/-/g, " ");
}
