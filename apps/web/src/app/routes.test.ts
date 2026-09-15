import { describe, expect, it } from "vitest";
import nextConfig from "../../next.config";
import { existsSync } from "node:fs";
import path from "node:path";

describe("canonical route redirects", () => {
  it("redirects legacy non-Beacon routes once without loops", async () => {
    const redirects = await nextConfig.redirects!();
    const expected = new Map([
      ["/harbor", "/flagships/harbor"],
      ["/initiatives", "/flagships"],
      ["/initiatives/haven", "/flagships/haven"],
      ["/projects", "/flagships"],
      ["/projects/community-aid-hub", "/flagships/harbor"],
      ["/projects/health-navigator", "/flagships/haven"],
    ]);

    for (const [source, destination] of expected) {
      expect(redirects).toContainEqual({ source, destination, permanent: true });
      expect(redirects.some((redirect) => redirect.source === destination)).toBe(false);
    }
  });

  it("does not reactivate removed Beacon routes", async () => {
    const redirects = await nextConfig.redirects!();
    expect(redirects.every((redirect) => !redirect.source.includes("beacon"))).toBe(true);
    expect(
      redirects.every(
        (redirect) => redirect.source !== "/projects/humanitarian-automation-pipeline",
      ),
    ).toBe(true);
    for (const removed of [
      "beacon", "initiatives/beacon", "projects/humanitarian-automation-pipeline",
    ]) {
      expect(existsSync(path.join(__dirname, removed, "page.tsx"))).toBe(false);
    }
    expect(existsSync(path.join(__dirname, "flagships", "beacon", "page.tsx"))).toBe(true);
  });
});
