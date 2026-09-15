import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HavenFlagshipPage from "./page";

describe("canonical Haven flagship", () => {
  it("uses the shared case-study structure and preserves safety and demo behavior", () => {
    render(<HavenFlagshipPage />);

    for (const heading of [
      "Module Purpose",
      "How it fits Zion",
      "Architecture Summary",
      "Boundaries and Limitations",
      "Demo and Evidence",
      "Interview Story",
    ]) {
      expect(screen.getByRole("heading", { name: heading })).toBeVisible();
    }
    const emergency = screen.getByRole("region", { name: "Emergency help" });
    expect(within(emergency).getByText(/call 911/i)).toBeVisible();
    expect(within(emergency).getByText(/call or text 988/i)).toBeVisible();
    expect(screen.getByRole("form", { name: "Synthetic concern demonstration" })).toBeVisible();
  });
});
