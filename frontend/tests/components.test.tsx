import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EmptyState, MetricCard } from "../components/ui";
import { money } from "../lib/format";
describe("public components", () => {
  it("labels unavailable values instead of displaying zero", () => {
    expect(money(null)).toBe("Dato no disponible");
    render(<EmptyState />);
    expect(screen.getByText(/no representa un valor de cero/i)).toBeInTheDocument();
  });
  it("renders accessible metric content", () => {
    render(<MetricCard label="Cobertura" value="Parcial" />);
    expect(screen.getByText("Cobertura")).toBeInTheDocument();
  });
});
