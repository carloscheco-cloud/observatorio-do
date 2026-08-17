import Link from "next/link";

import { SearchBar } from "@/components/SearchBar";
import { MethodologyNotice, MetricCard } from "@/components/ui";
import { api, optional } from "@/lib/api";
import {
  branchLabels,
  branchRoutes,
  getStateCoverage,
  totalStateInstitutions,
  type StateBranch,
} from "@/lib/state-api";

interface Metrics {
  data: Record<string, number | null>;
  generated_at: string;
}

const branches: StateBranch[] = ["executive", "legislative", "judicial"];

export default async function Home() {
  const [coverage, metrics] = await Promise.all([
    optional(getStateCoverage()),
    optional(api<Metrics>("/metrics")),
  ]);
  const stateTotal = coverage ? totalStateInstitutions(coverage) : null;

  return <>
    <section className="hero"><div className="shell">
      <p className="eyebrow">Información pública para comprender el Estado</p>
      <h1>El Estado dominicano, cada vez más visible.</h1>
      <p className="lede">Explora instituciones, autoridades, empleo, presupuesto, compras, deuda y patrimonio. La cobertura se amplía de manera continua y conserva sus fuentes.</p>
      <SearchBar />
    </div></section>

    <section className="section shell">
      <p className="eyebrow">Cobertura canónica viva</p>
      <h2>Los tres poderes</h2>
      <div className="grid metrics">
        <MetricCard
          label="Instituciones documentadas"
          value={stateTotal ?? "No disponible"}
          note="Suma de instituciones confirmadas en Ejecutivo, Legislativo y Judicial"
        />
        {branches.map((branch) => (
          <MetricCard
            key={branch}
            label={branchLabels[branch]}
            value={coverage?.branches[branch].institutions ?? "No disponible"}
            note={coverage ? `Cobertura básica ${Math.round(coverage.branches[branch].basic_ratio * 100)}%` : undefined}
          />
        ))}
      </div>
      <div className="grid">
        {branches.map((branch) => (
          <Link className="card" href={branchRoutes[branch]} key={branch}>
            <p className="eyebrow">{branchLabels[branch]}</p>
            <h3>{coverage?.branches[branch].institutions ?? "—"} instituciones</h3>
            <p>Consulta el directorio confirmado y sigue cómo cada ficha gana profundidad documental.</p>
          </Link>
        ))}
      </div>
      <aside className="notice">
        <strong>Cómo leer estas cifras</strong>
        <p>
          “Documentada” significa que la institución está confirmada en la base canónica con la
          cobertura pública disponible. No significa que todas sus dimensiones estén completas ni
          constituye una evaluación de desempeño, legalidad u honestidad.
        </p>
      </aside>
    </section>

    <section className="section shell">
      <h2>Panorama público por tema</h2>
      <div className="grid">
        {Object.entries(metrics?.data ?? {}).map(([label, value]) => (
          <MetricCard key={label} label={label} value={value ?? "No disponible"} />
        ))}
        {!metrics && <MetricCard label="Cobertura temática" value="No disponible" note="La ausencia no representa cero" />}
      </div>
      <MethodologyNotice />
    </section>

    <section className="section shell"><h2>Explora por tema</h2><div className="grid">
      {[["/nomina","Nómina"],["/presupuesto","Presupuesto"],["/compras","Compras"],["/deuda","Deuda"],["/patrimonio","Patrimonio"],["/fuentes","Fuentes"]].map(([href,label])=>
        <Link className="card" href={href} key={href}><h3>{label}</h3><p>Consulta cobertura, evolución y fuentes públicas.</p></Link>
      )}
    </div></section>
  </>;
}
