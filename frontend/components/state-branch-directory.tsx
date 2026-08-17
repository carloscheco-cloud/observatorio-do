import Link from "next/link";

import { EmptyState } from "@/components/ui";
import { api, optional } from "@/lib/api";

interface BranchInstitution {
  id: string;
  name: string;
  kind: string;
  acronym: string | null;
  slug: string | null;
  state_branch: string;
  institution_type: string | null;
  operational_status: string;
  coverage_level: string;
  official_website: string | null;
}

interface BranchResponse {
  data: BranchInstitution[];
  pagination: { page: number; page_size: number; total_items: number };
  filters_applied: { branch: string };
  warnings: string[];
}

export async function StateBranchDirectory({
  branch,
  title,
  description,
}: {
  branch: "legislative" | "judicial";
  title: string;
  description: string;
}) {
  const response = await optional(
    api<BranchResponse>(`/state/institutions?branch=${branch}&page_size=250`),
  );
  const institutions = response?.data ?? [];

  return (
    <div className="shell section">
      <p className="eyebrow">Observatorio del Estado Dominicano</p>
      <h1>{title}</h1>
      <p className="lede">{description}</p>
      <p className="card">
        Instituciones visibles: <strong>{response?.pagination.total_items ?? 0}</strong>. La cobertura
        se amplía y audita de manera continua.
      </p>
      {institutions.length > 0 ? (
        <div className="grid">
          {institutions.map((institution) => (
            <Link className="card" key={institution.id} href={`/instituciones/${institution.id}`}>
              <p className="eyebrow">{institution.acronym ?? institution.kind}</p>
              <h3>{institution.name}</h3>
              <p>
                Cobertura: {institution.coverage_level} · Estado: {institution.operational_status}
              </p>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState title="La compañía autónoma todavía está construyendo esta rama del Estado" />
      )}
    </div>
  );
}
