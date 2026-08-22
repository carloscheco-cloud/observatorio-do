import type { Metadata } from "next";

import { PowerObservationMap } from "@/components/power-observation-map";
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
    <>
      <section className="hero">
        <div className="shell">
          <p className="eyebrow">Representación, actividad y trazabilidad</p>
          <h1>Poder Legislativo</h1>
          <p className="lede">
            El OED seguirá no solo las instituciones legislativas, sino también quién representa a
            cada territorio, su partido actual e histórico, trayectoria, asistencia, comisiones,
            iniciativas, votaciones, leyes, declaraciones juradas y beneficios públicos documentados.
          </p>
        </div>
      </section>

      <PowerObservationMap branch="legislative" />

      <StateBranchDirectory
        branch="legislative"
        title="Directorio del Poder Legislativo"
        description="Senado, Cámara de Diputados y demás instituciones legislativas incorporadas con fuentes públicas trazables. La cobertura personal y parlamentaria se agregará sobre esta base institucional."
        searchParams={await searchParams}
        compactHeader
      />
    </>
  );
}
