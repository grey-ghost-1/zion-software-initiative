import { describe, expect, it } from "vitest";
import { flagshipModules, getFlagshipModule } from "./flagships";

describe("flagship content catalog", () => {
  it("contains exactly the two shipping modules with complete evidence and stories", () => {
    expect(flagshipModules.map((module) => module.id)).toEqual(["harbor", "haven"]);

    for (const flagship of flagshipModules) {
      expect(flagship.purpose).toBeTruthy();
      expect(flagship.fit).toBeTruthy();
      expect(flagship.architecture).toMatch(/Next\.js/i);
      expect(flagship.boundaries.length).toBeGreaterThanOrEqual(4);
      expect(flagship.evidence.length).toBeGreaterThanOrEqual(3);
      expect(Object.values(flagship.interviewStory).every(Boolean)).toBe(true);
      expect(flagship.status.operational).toBe("not-operational");
    }
  });

  it("does not include the concurrently retired module", () => {
    const excludedModuleName = ["Bea", "con"].join("");
    expect(JSON.stringify(flagshipModules)).not.toContain(excludedModuleName);
  });

  it("returns catalog entries by typed identifier", () => {
    expect(getFlagshipModule("harbor").route).toBe("/harbor");
    expect(getFlagshipModule("haven").route).toBe("/initiatives/haven");
  });
});
