import type { Metadata } from "next";

import { StateBranchDirectory } from "@/components/state-branch-directory";

export const metadata: Metadata = {
  title: "Poder Legislativo",
  description: "Directorio vivo de instituciones del Poder Legislativo documentadas por el OED.",
  alternates: { canonical: "/poder-legislativo" },
};

type SearchParams = Record<string, string | string[] | undefined>;

export default async function LegislativeBranchPage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  return (
    <StateBranchDirectory
      branch="legislative"
      title="Poder Legislativo"
      description="Senado, Cámara de Diputados y las instituciones legislativas incorporadas por el OED con fuentes públicas trazables."
      searchParams={await searchParams}
    />
  );
}
