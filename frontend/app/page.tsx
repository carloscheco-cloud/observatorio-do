import Link from "next/link";
import { SearchBar } from "@/components/SearchBar";
import { MethodologyNotice, MetricCard } from "@/components/ui";
import { api, optional } from "@/lib/api";

interface Metrics {
  data: Record<string, number | null>;
  generated_at: string;
}

export default async function Home() {
  const metrics = await optional(api<Metrics>("/metrics"));
  return <>
    <section className="hero"><div className="shell">
      <p className="eyebrow">Información pública para comprender el Estado</p>
      <h1>Datos trazables. Consulta ciudadana clara.</h1>
      <p className="lede">Explora instituciones, empleo, presupuesto, compras, deuda y patrimonio sin exponer información interna o sensible.</p>
      <SearchBar />
    </div></section>
    <section className="section shell">
      <h2>Panorama público</h2>
      <div className="grid">
        {Object.entries(metrics?.data ?? {}).map(([label, value]) => (
          <MetricCard key={label} label={label} value={value ?? "No disponible"} />
        ))}
        {!metrics && <MetricCard label="Cobertura" value="No disponible" note="La ausencia no representa cero" />}
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
