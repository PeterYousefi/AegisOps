import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { AssessmentPanel } from "@/components/ai/assessment-panel";
import type { Assessment } from "@/lib/types";

const ASSESSMENT: Assessment = {
  id: "a1",
  incident_id: "i1",
  provider: "mock",
  executive_summary: "Checkout failing after deploy.",
  severity: "sev1",
  affected_services: ["checkout-api"],
  likely_root_cause: "Timeout reduced by deploy.",
  confidence_score: 0.85,
  evidence_references: ["ev-123"],
  runbook_references: ["rb-456"],
  recommended_next_steps: ["Roll back"],
  uncertainties: [],
  safety_notes: ["Human approval required"],
  validation_status: "valid",
  created_at: "2026-09-16T00:00:00Z",
};

describe("AssessmentPanel", () => {
  it("renders summary, root cause, confidence and citations", () => {
    render(<AssessmentPanel assessment={ASSESSMENT} />);
    expect(screen.getByText("Checkout failing after deploy.")).toBeInTheDocument();
    expect(screen.getByText(/85% confidence/)).toBeInTheDocument();
    expect(screen.getByText(/evidence:ev-123/)).toBeInTheDocument();
    expect(screen.getByText(/runbook:rb-456/)).toBeInTheDocument();
  });

  it("evidence citation scrolls to the referenced evidence element", () => {
    // Render the target evidence element the citation should resolve to.
    const target = document.createElement("li");
    target.id = "evidence-ev-123";
    target.scrollIntoView = vi.fn();
    document.body.appendChild(target);

    render(<AssessmentPanel assessment={ASSESSMENT} />);
    fireEvent.click(screen.getByText(/evidence:ev-123/));
    expect(target.scrollIntoView).toHaveBeenCalled();

    document.body.removeChild(target);
  });

  it("shows a fallback warning for invalid assessments", () => {
    render(
      <AssessmentPanel
        assessment={{ ...ASSESSMENT, validation_status: "invalid_fallback" }}
      />,
    );
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });
});
