import { api } from "./api";

export type StateBranch = "executive" | "legislative" | "judicial";

export interface BranchCoverage {
  branch: StateBranch;
  institutions: number;
  basic_or_better: number;
  substantial_or_better: number;
  basic_ratio: number;
  substantial_ratio: number;
}

export interface StateCoverageResponse {
  mission: string;
  autonomy_enabled: boolean;
  target_basic_coverage: number;
  next_focus: StateBranch | null;
  branches: Record<StateBranch, BranchCoverage>;
  operating_rule: string;
}

export interface StateInstitution {
  id: string;
  name: string;
  kind: string;
  acronym: string | null;
  slug: string | null;
  state_branch: StateBranch;
  institution_type: string | null;
  operational_status: string;
  coverage_level: string;
  official_website: string | null;
}

export interface StateInstitutionResponse {
  data: StateInstitution[];
  pagination: {
    page: number;
    page_size: number;
    total_items: number;
  };
  filters_applied: { branch: StateBranch };
  warnings: string[];
}

export const branchLabels: Record<StateBranch, string> = {
  executive: "Poder Ejecutivo",
  legislative: "Poder Legislativo",
  judicial: "Poder Judicial",
};

export const branchRoutes: Record<StateBranch, string> = {
  executive: "/poder-ejecutivo",
  legislative: "/poder-legislativo",
  judicial: "/poder-judicial",
};

export function coverageLabel(level: string): string {
  const labels: Record<string, string> = {
    basic: "Ficha básica verificada",
    partial: "Cobertura parcial",
    substantial: "Cobertura sustancial",
    complete: "Cobertura completa",
  };
  return labels[level] ?? level;
}

export function institutionTypeLabel(type: string | null, kind: string): string {
  if (!type) return kind;
  const labels: Record<string, string> = {
    ministry: "Ministerio",
    presidency: "Presidencia",
    vice_presidency: "Vicepresidencia",
    directorate: "Dirección",
    institute: "Instituto",
    council: "Consejo",
    commission: "Comisión",
    corporation: "Empresa pública",
    court: "Tribunal",
    chamber: "Cámara",
  };
  return labels[type] ?? type.replaceAll("_", " ");
}

export function totalStateInstitutions(coverage: StateCoverageResponse): number {
  return Object.values(coverage.branches).reduce(
    (total, branch) => total + branch.institutions,
    0,
  );
}

export const getStateCoverage = () => api<StateCoverageResponse>("/state/coverage");

export const getStateInstitutions = (branch: StateBranch) =>
  api<StateInstitutionResponse>(`/state/institutions?branch=${branch}&page_size=250`);
