import type { Metadata } from "next";

import { StateBranchDirectory } from "@/components/state-branch-directory";

export const metadata: Metadata = {
  title: "Poder Judicial",
  description: "Directorio vivo de instituciones del Poder Judicial documentadas por el OED.",
  alternates: { canonical: "/poder-judicial" },
};

type SearchParams = Record<string, string | string[] | undefined>;

export default async function JudicialBranchPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  return (
    <StateBranchDirectory
      branch="judicial"
      title="Poder Judicial"
      description="Suprema Corte de Justicia, Consejo del Poder Judicial, cortes, tribunales y demás estructura judicial incorporada por el OED con fuentes públicas trazables."
      searchParams={await searchParams}
    />
  );
}
