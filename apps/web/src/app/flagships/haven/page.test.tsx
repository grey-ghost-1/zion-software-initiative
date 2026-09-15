import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HavenFlagshipPage from "./page";

describe("canonical Haven flagship", () => {
  it("uses the shared case-study structure and preserves safety and demo behavior", () => {
    render(<HavenFlagshipPage />);

    for (const heading of [
      "Module purpose",
      "How it fits Zion",
      "Architecture summary",
      "Safety boundaries",
      "Demo and Evidence",
      "Interview story",
      "Technical highlights",
      "GitHub links",
    ]) {
      expect(screen.getByRole("heading", { name: heading })).toBeVisible();
    }
    const emergency = screen.getByRole("region", { name: "Emergency help" });
    expect(within(emergency).getByText(/call 911/i)).toBeVisible();
    expect(within(emergency).getByText(/call or text 988/i)).toBeVisible();
    expect(screen.getByRole("form", { name: "Synthetic concern demonstration" })).toBeVisible();
    expect(screen.getByText(/content-preservation validation protects critical source facts/i)).toBeVisible();
    expect(screen.getByText(/implemented slice demonstrates explainable navigation/i)).toBeVisible();
    expect(screen.queryByText(/placeholder/i)).not.toBeInTheDocument();
  });
});
