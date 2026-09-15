import { render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import MissionPage from "./page";

describe("mission page", () => {
  it("presents one accessible mission for public and recruiter audiences", () => {
    render(<MissionPage />);

    expect(screen.getByRole("main")).toBeInTheDocument();
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByRole("heading", { name: /human judgment stays/i })).toBeVisible();
    expect(screen.getByText("For the public")).toBeVisible();
    expect(
      screen.getByRole("heading", { name: /portfolio thesis/i }),
    ).toBeVisible();
    expect(
      within(screen.getByRole("navigation", { name: "Mission evidence" })).getAllByRole(
        "link",
      ),
    ).toHaveLength(3);
  });

  it("states non-operational and safety boundaries", () => {
    render(<MissionPage />);

    expect(screen.getByText(/not deployed, production-verified/i)).toBeVisible();
    expect(screen.getByText(/synthetic data and deterministic safety rules/i)).toBeVisible();
    expect(screen.getByText(/not an emergency or autonomous dispatch service/i)).toBeVisible();
    expect(screen.getByText(/provides no diagnosis, treatment, or medical advice/i)).toBeVisible();
  });
});
