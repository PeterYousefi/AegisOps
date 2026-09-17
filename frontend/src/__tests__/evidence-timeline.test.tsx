import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { EvidenceTimeline } from "@/components/evidence/evidence-timeline";
import type { EvidenceRecord } from "@/lib/types";

const EVIDENCE: EvidenceRecord[] = [
  {
    id: "e1",
    incident_id: "i1",
    evidence_type: "alert",
    source: "monitoring",
    summary: "Alert fired",
    payload: { k: "v" },
    observed_at: "2026-09-15T14:00:00Z",
    created_at: "2026-09-15T14:00:00Z",
  },
  {
    id: "e2",
    incident_id: "i1",
    evidence_type: "deployment",
    source: "deploys",
    summary: "Release deployed",
    payload: {},
    observed_at: "2026-09-15T13:59:00Z",
    created_at: "2026-09-15T13:59:00Z",
  },
];

describe("EvidenceTimeline", () => {
  it("renders all evidence by default", () => {
    render(<EvidenceTimeline evidence={EVIDENCE} />);
    expect(screen.getByText("Alert fired")).toBeInTheDocument();
    expect(screen.getByText("Release deployed")).toBeInTheDocument();
  });

  it("filters by evidence type", () => {
    render(<EvidenceTimeline evidence={EVIDENCE} />);
    fireEvent.change(screen.getByLabelText("Filter evidence by type"), {
      target: { value: "alert" },
    });
    expect(screen.getByText("Alert fired")).toBeInTheDocument();
    expect(screen.queryByText("Release deployed")).not.toBeInTheDocument();
  });

  it("gives each evidence item a stable dom id for citations", () => {
    const { container } = render(<EvidenceTimeline evidence={EVIDENCE} />);
    expect(container.querySelector("#evidence-e1")).not.toBeNull();
    expect(container.querySelector("#evidence-e2")).not.toBeNull();
  });
});
