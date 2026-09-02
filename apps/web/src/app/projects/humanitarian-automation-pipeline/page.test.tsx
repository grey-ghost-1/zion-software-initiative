import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import HumanitarianAutomationPipelinePage from "./page";

describe("Humanitarian Automation Pipeline page", () => {
  it("shows the route as a first-class project page", () => {
    render(<HumanitarianAutomationPipelinePage />);

    const nav = screen.getByRole("navigation", { name: "Primary" });
    expect(within(nav).getByRole("link", { name: "Projects" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByText("Purpose")).toBeVisible();
    expect(screen.getByText("Audience")).toBeVisible();
    expect(screen.getByText("Features")).toBeVisible();
    expect(screen.getByText("Limitations")).toBeVisible();
    expect(screen.getByRole("heading", { name: "Evidence" })).toBeVisible();
    expect(screen.getByRole("link", { name: "Back to projects index" })).toHaveAttribute(
      "href",
      "/projects",
    );
    expect(screen.getByRole("link", { name: "Community Aid Hub" })).toHaveAttribute(
      "href",
      "/projects/community-aid-hub",
    );
    expect(screen.getByText(/no real disasters, dispatch, purchasing/i)).toBeVisible();
  });
});
