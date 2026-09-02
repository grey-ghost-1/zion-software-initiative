import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import BeaconPage from "./page";

describe("Beacon page", () => {
  it("keeps one h1 and marks Initiatives as the current nav section", () => {
    render(<BeaconPage />);

    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    const nav = screen.getByRole("navigation", { name: "Primary" });
    expect(within(nav).getByRole("link", { name: "Initiatives" })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });

  it("discloses the synthetic, exploratory, no-official-warning status", () => {
    render(<BeaconPage />);

    const disclosure = screen.getByText(/synthetic, exploratory demonstration/i);
    expect(disclosure).toBeVisible();
    expect(screen.getByText(/issues no warnings/i)).toBeVisible();
    expect(screen.getByText(/National Weather Service/)).toBeVisible();
  });

  it("renders the pipeline as both a list and an equivalent data table", () => {
    render(<BeaconPage />);

    const table = screen.getByRole("table", {
      name: "Typed workflow steps and outcomes (tabular equivalent)",
    });
    const rows = within(table).getAllByRole("row");
    expect(rows.length).toBe(8); // header + 7 steps
    // Status is conveyed as text, not only color.
    expect(within(table).getByText("Paused for human decision")).toBeVisible();
    expect(screen.getAllByText(/await_human_approval/).length).toBeGreaterThanOrEqual(2);
  });

  it("shows the explainable allocation table with reasons and unmet demand", () => {
    render(<BeaconPage />);

    const table = screen.getByRole("table", {
      name: "Excerpt of one recorded allocation proposal",
    });
    expect(
      within(table).getByText(/below the activation threshold/),
    ).toBeVisible();
    expect(within(table).getByText(/inventory exhausted/)).toBeVisible();
    expect(screen.getByText(/no optimality guarantee/)).toBeVisible();
  });
});
