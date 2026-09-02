import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { LabsArchive } from "./labs";

const SNAPSHOT_PATH = join(
  process.cwd(),
  "..",
  "..",
  "docs",
  "evidence",
  "zion-labs-prior-work.json",
);

export function loadLabsArchive(): LabsArchive {
  const raw = readFileSync(SNAPSHOT_PATH, "utf-8");
  return JSON.parse(raw) as LabsArchive;
}
