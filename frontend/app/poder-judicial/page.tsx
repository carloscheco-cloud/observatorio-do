import type { Metadata } from "next";

import { PowerObservationMap } from "@/components/power-observation-map";
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
    <>
      <section className="hero">
        <div className="shell">
          <p className="eyebrow">Estructura, magistrados y decisiones públicas</p>
          <h1>Poder Judicial</h1>
          <p className="lede">
            El OED documentará la estructura judicial, sus jueces y magistrados, formación,
            trayectoria, mecanismo de designación, decisiones públicas relevantes y recursos
            institucionales, siempre con fuentes documentales y sin evaluaciones personales.
          </p>
        </div>
      </section>

      <PowerObservationMap branch="judicial" />

      <StateBranchDirectory
        branch="judicial"
        title="Directorio del Poder Judicial"
        description="Suprema Corte de Justicia, Consejo del Poder Judicial, cortes, tribunales y demás estructura judicial confirmada. Sobre esta base se incorporarán perfiles, designaciones, decisiones y recursos públicos trazables."
        searchParams={await searchParams}
        compactHeader
      />
    </>
  );
}
