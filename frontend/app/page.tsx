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
      <h1>El Estado dominicano, cada vez más visible.</h1>
      <p className="lede">Explora instituciones, autoridades, empleo, presupuesto, compras, deuda y patrimonio. La cobertura se amplía de manera continua y conserva sus fuentes.</p>
      <SearchBar />
    </div></section>
    <section className="section shell">
      <h2>Los tres poderes</h2>
      <div className="grid">
        <Link className="card" href="/poder-ejecutivo"><p className="eyebrow">Poder Ejecutivo</p><h3>Presidencia, ministerios e instituciones</h3><p>Explora la rama con mayor cobertura actual del OED.</p></Link>
        <Link className="card" href="/poder-legislativo"><p className="eyebrow">Poder Legislativo</p><h3>Congreso Nacional</h3><p>Senado, Cámara de Diputados y estructura legislativa.</p></Link>
        <Link className="card" href="/poder-judicial"><p className="eyebrow">Poder Judicial</p><h3>Tribunales y estructura judicial</h3><p>Suprema Corte, Consejo del Poder Judicial y tribunales.</p></Link>
      </div>
    </section>
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
