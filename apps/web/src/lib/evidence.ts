import { readFileSync } from "node:fs";
import { join } from "node:path";

export interface EvidenceClaim {
  id: string;
  claim: string;
  status: "implemented";
  evidence: string;
  verified_by: string;
}

interface EvidenceInventory {
  claims: EvidenceClaim[];
}

/**
 * Reads the repository's evidence inventory (the same file the root test
 * suite validates against its JSON schema) so this page can never drift from
 * what `docs/evidence/inventory.json` actually says.
 */
export function loadEvidenceClaims(): EvidenceClaim[] {
  const inventoryPath = join(process.cwd(), "..", "..", "docs", "evidence", "inventory.json");
  const raw = readFileSync(inventoryPath, "utf-8");
  const inventory = JSON.parse(raw) as EvidenceInventory;
  return inventory.claims;
}
