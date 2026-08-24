import type { Metadata } from "next";
import Link from "next/link";

import { PowerObservationMap } from "@/components/power-observation-map";
import { SenateDirectory } from "@/components/senate-directory";
import { StateBranchDirectory } from "@/components/state-branch-directory";

export const metadata: Metadata = {
  title: "Poder Legislativo",
  description: "Senadores, diputados e instituciones del Poder Legislativo documentados por el OED.",
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
            El OED documenta quién representa a cada territorio y, progresivamente, su formación,
            partido, trayectoria, asistencia, comisiones, iniciativas, votaciones, declaraciones y
            beneficios públicos, conservando las fuentes de cada dato.
          </p>
          <p className="senator-links">
            <a className="button" href="#senadores">Ver los 32 senadores</a>
            <Link className="button secondary" href="/poder-legislativo/ranking-integral">Ranking integral de los 32</Link>
            <Link className="button secondary" href="/poder-legislativo/asistencia">Ranking de asistencia y comisiones</Link>
            <Link className="button secondary" href="/poder-legislativo/produccion-legislativa">Leyes e iniciativas por senador</Link>
            <Link className="button secondary" href="/poder-legislativo/patrimonio">Patrimonio y declaraciones juradas</Link>
            <Link className="button secondary" href="/poder-legislativo/patrimonio/evolucion">Evolución patrimonial histórica</Link>
          </p>
        </div>
      </section>

      <SenateDirectory />

      <PowerObservationMap branch="legislative" />

      <StateBranchDirectory
        branch="legislative"
        title="Instituciones del Poder Legislativo"
        description="Senado, Cámara de Diputados y demás instituciones legislativas incorporadas con fuentes públicas trazables. El directorio personal se construye sobre esta base institucional."
        searchParams={await searchParams}
        compactHeader
      />
    </>
  );
}