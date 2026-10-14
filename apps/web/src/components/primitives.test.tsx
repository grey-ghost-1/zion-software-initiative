import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { CaseStudyCard, StatusBadge } from "@zion/ui";

describe("StatusBadge", () => {
  it("renders the truthful label for each status", () => {
    render(
      <>
        <StatusBadge status="implemented" />
        <StatusBadge status="in-development" />
        <StatusBadge status="planned" />
      </>,
    );

    expect(screen.getByText("Implemented")).toBeVisible();
    expect(screen.getByText("In development")).toBeVisible();
    expect(screen.getByText("Planned")).toBeVisible();
  });

  it("allows an explicit label override while keeping the status class", () => {
    const { container } = render(<StatusBadge status="planned" label="Not started" />);

    expect(screen.getByText("Not started")).toBeVisible();
    expect(container.querySelector(".status-badge--planned")).not.toBeNull();
  });
});

describe("CaseStudyCard", () => {
  it("labels the impact and engineering variants distinctly", () => {
    render(
      <>
        <CaseStudyCard
          variant="impact"
          title="Impact title"
          status="planned"
          summary="Impact summary"
        />
        <CaseStudyCard
          variant="engineering"
          title="Engineering title"
          status="implemented"
          summary="Engineering summary"
        />
      </>,
    );

    expect(screen.getByText("Impact case study")).toBeVisible();
    expect(screen.getByText("Engineering case study")).toBeVisible();
    expect(screen.getByRole("heading", { name: "Impact title" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Engineering title" })).toBeVisible();
  });

  it("only renders an evidence link when a details href is provided", () => {
    const { rerender } = render(
      <CaseStudyCard variant="engineering" title="No link" status="planned" summary="s" />,
    );
    expect(screen.queryByRole("link")).not.toBeInTheDocument();

    rerender(
      <CaseStudyCard
        variant="engineering"
        title="With link"
        status="implemented"
        summary="s"
        detailsHref="/evidence"
        detailsLabel="See evidence"
      />,
    );
    expect(screen.getByRole("link", { name: "See evidence" })).toHaveAttribute(
      "href",
      "/evidence",
    );
  });
});
