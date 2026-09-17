import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { IncidentFilters } from "@/components/incidents/incident-filters";

describe("IncidentFilters", () => {
  it("renders status and severity selects", () => {
    render(<IncidentFilters value={{}} onChange={() => {}} />);
    expect(screen.getByLabelText("Filter by status")).toBeInTheDocument();
    expect(screen.getByLabelText("Filter by severity")).toBeInTheDocument();
  });

  it("calls onChange with the selected status", () => {
    const onChange = vi.fn();
    render(<IncidentFilters value={{}} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText("Filter by status"), {
      target: { value: "investigating" },
    });
    expect(onChange).toHaveBeenCalledWith({ status: "investigating" });
  });

  it("calls onChange with the selected severity", () => {
    const onChange = vi.fn();
    render(<IncidentFilters value={{}} onChange={onChange} />);
    fireEvent.change(screen.getByLabelText("Filter by severity"), {
      target: { value: "sev1" },
    });
    expect(onChange).toHaveBeenCalledWith({ severity: "sev1" });
  });

  it("shows a clear button only when a filter is active and clears on click", () => {
    const onChange = vi.fn();
    const { rerender } = render(
      <IncidentFilters value={{}} onChange={onChange} />,
    );
    expect(screen.queryByText("Clear filters")).not.toBeInTheDocument();

    rerender(
      <IncidentFilters value={{ severity: "sev1" }} onChange={onChange} />,
    );
    const clear = screen.getByText("Clear filters");
    fireEvent.click(clear);
    expect(onChange).toHaveBeenCalledWith({});
  });
});
