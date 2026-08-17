import { describe, expect, it } from "vitest";

import {
  coverageLabel,
  institutionTypeLabel,
  totalStateInstitutions,
  type StateCoverageResponse,
} from "../lib/state-api";

const coverage: StateCoverageResponse = {
  mission: "Cobertura pública verificable",
  autonomy_enabled: true,
  target_basic_coverage: 0.8,
  next_focus: "executive",
  operating_rule: "Cobertura primero",
  branches: {
    executive: {
      branch: "executive",
      institutions: 195,
      basic_or_better: 195,
      substantial_or_better: 0,
      basic_ratio: 1,
      substantial_ratio: 0,
    },
    legislative: {
      branch: "legislative",
      institutions: 41,
      basic_or_better: 41,
      substantial_or_better: 0,
      basic_ratio: 1,
      substantial_ratio: 0,
    },
    judicial: {
      branch: "judicial",
      institutions: 30,
      basic_or_better: 30,
      substantial_or_better: 0,
      basic_ratio: 1,
      substantial_ratio: 0,
    },
  },
};

describe("state public surface helpers", () => {
  it("sums the three live branches", () => {
    expect(totalStateInstitutions(coverage)).toBe(266);
  });

  it("uses citizen-facing coverage labels", () => {
    expect(coverageLabel("basic")).toBe("Ficha básica verificada");
    expect(coverageLabel("complete")).toBe("Cobertura completa");
  });

  it("uses readable institution type labels", () => {
    expect(institutionTypeLabel("ministry", "agency")).toBe("Ministerio");
    expect(institutionTypeLabel(null, "agency")).toBe("agency");
  });
});
