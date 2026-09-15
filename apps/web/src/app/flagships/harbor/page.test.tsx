import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HarborFlagshipPage from "./page";

describe("canonical Harbor flagship", () => {
  it("uses the shared case-study structure and preserves the workflow", () => {
    render(<HarborFlagshipPage />);

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
    expect(screen.getByRole("heading", { name: "Capacity and approval controls" })).toBeVisible();
    expect(screen.getByText(/unknown or stale capacity is unavailable/i)).toBeVisible();
    expect(screen.getByText(/coordinator explicitly reviews and approves/i)).toBeVisible();
    expect(screen.getByRole("form", { name: "Synthetic Harbor workflow" })).toBeVisible();
    expect(screen.getByText(/deterministic matching exposes score components/i)).toBeVisible();
    expect(screen.getByText(/implemented slice makes a proposed match inspectable/i)).toBeVisible();
    expect(screen.queryByText(/placeholder/i)).not.toBeInTheDocument();
  });
});
