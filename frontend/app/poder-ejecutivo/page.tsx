import type { Metadata } from "next";
import Link from "next/link";

import { ExecutiveNav } from "@/components/executive";
import { PowerObservationMap } from "@/components/power-observation-map";
import { StateBranchDirectory } from "@/components/state-branch-directory";

export const metadata: Metadata = {
  title: "Poder Ejecutivo",
  description: "Directorio vivo del Poder Ejecutivo dominicano documentado por el OED.",
  alternates: { canonical: "/poder-ejecutivo" },
  openGraph: {
    title: "Poder Ejecutivo",
    description: "Consulta instituciones confirmadas y su cobertura pública en el OED.",
  },
};

type SearchParams = Record<string, string | string[] | undefined>;

export default async function ExecutivePage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  return (
    <>
      <section className="hero">
        <div className="shell">
          <p className="eyebrow">Cobertura pública viva</p>
          <h1>Poder Ejecutivo</h1>
          <p className="lede">
            Explora las instituciones confirmadas del Poder Ejecutivo y sigue, por institución,
            quién la dirige, cuánto presupuesto recibe, cuánto ejecuta, su nómina, sus compras,
            proveedores, contratos y la evidencia pública disponible.
          </p>
          <ExecutiveNav />
        </div>
      </section>

      <PowerObservationMap branch="executive" />

      <StateBranchDirectory
        branch="executive"
        title="Directorio completo del Ejecutivo"
        description="Instituciones confirmadas actualmente disponibles en el OED. Cada ficha se irá enriqueciendo con autoridades, presupuesto, ejecución, nómina, compras, patrimonio y fuentes trazables."
        searchParams={await searchParams}
        compactHeader
      />

      <section className="shell section">
        <h2>Profundidad documental</h2>
        <div className="grid">
          <Link className="card" href="/poder-ejecutivo/documentacion">
            <p className="eyebrow">Capa ampliada</p>
            <h3>Documentación y evaluación</h3>
            <p>
              Consulta las instituciones que ya tienen autoridad, evaluación documental y otras
              dimensiones incorporadas por las fases profundas del OED.
            </p>
          </Link>
          <Link className="card" href="/poder-ejecutivo/autoridades">
            <p className="eyebrow">Personas y cargos</p>
            <h3>Autoridades</h3>
            <p>Consulta autoridades actuales, actos de designación y evidencia disponible.</p>
          </Link>
          <Link className="card" href="/poder-ejecutivo/cambios">
            <p className="eyebrow">Historia pública</p>
            <h3>Cambios recientes</h3>
            <p>Consulta eventos persistidos sin convertir cambios técnicos en noticias políticas.</p>
          </Link>
        </div>
      </section>
    </>
  );
}
