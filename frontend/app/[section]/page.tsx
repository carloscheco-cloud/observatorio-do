import type { Metadata } from "next";
import Link from "next/link";
import { DataTable, EmptyState, ExportButton, MethodologyNotice } from "@/components/ui";
import { TimeSeriesChart } from "@/components/charts";
import { api, getInstitutions, optional } from "@/lib/api";
import type { Collection, Institution, Summary } from "@/types/public";

const sections: Record<string, { title: string; description: string; endpoint?: string }> = {
  instituciones: { title: "Instituciones", description: "Directorio de instituciones confirmadas y respaldadas por evidencia.", endpoint: "/institutions" },
  personas: { title: "Personas públicas", description: "Trayectorias públicas vinculadas a cargos y designaciones.", endpoint: "/persons" },
  territorios: { title: "Territorios", description: "Consulta territorial de instituciones, cobertura e indicadores.", endpoint: "/territories" },
  nomina: { title: "Nómina pública", description: "Empleo observado y masa salarial por períodos compatibles.", endpoint: "/payroll/evolution" },
  presupuesto: { title: "Presupuesto", description: "Apropiación, vigencia y ejecución con trazabilidad.", endpoint: "/budget/evolution" },
  compras: { title: "Compras públicas", description: "Procesos, contratos, pagos y proveedores.", endpoint: "/procurement/contracts" },
  contratos: { title: "Contratos", description: "Contratos públicos revisados y sus cambios históricos.", endpoint: "/procurement/contracts" },
  proveedores: { title: "Proveedores", description: "Proveedores canónicos sin identificadores registrales sensibles.", endpoint: "/procurement/suppliers" },
  deuda: { title: "Deuda pública", description: "Instrumentos, servicio y evolución de obligaciones públicas.", endpoint: "/debt/evolution" },
  patrimonio: { title: "Patrimonio público", description: "Activos públicos sin seriales ni ubicaciones restringidas.", endpoint: "/assets/evolution" },
  alertas: { title: "Alertas públicas", description: "Señales observables publicadas tras revisión humana.", endpoint: "/findings" },
  comparar: { title: "Comparar", description: "Compara instituciones con unidades y períodos compatibles." },
  fuentes: { title: "Fuentes", description: "Procedencia, frescura, cobertura y calidad de los datos.", endpoint: "/data-freshness" },
  metodologia: { title: "Metodología", description: "Cómo adquirimos, revisamos, publicamos y explicamos los datos.", endpoint: "/methodology" },
  acerca: { title: "Acerca del Observatorio", description: "Una iniciativa independiente para facilitar la consulta ciudadana." },
};

export async function generateMetadata({ params }: { params: Promise<{ section: string }> }): Promise<Metadata> {
  const { section } = await params;
  return { title: sections[section]?.title ?? "Consulta" };
}

function text(value: unknown): string {
  if (value === null || value === undefined) return "No disponible";
  return typeof value === "object" ? JSON.stringify(value) : String(value);
}

export default async function Section({ params }: { params: Promise<{ section: string }> }) {
  const { section } = await params;
  const item = sections[section];
  if (!item) return <div className="shell section"><EmptyState title="Página no encontrada" /></div>;
  const response = item.endpoint
    ? await optional(api<Collection<Record<string, unknown>> | Summary>(item.endpoint))
    : null;
  const institutions = section === "comparar" ? await optional(getInstitutions()) : null;
  const rows = response && "pagination" in response ? response.data : [];
  const summary = response && !("pagination" in response) ? response.data : null;
  const series = summary && Array.isArray(summary.series)
    ? summary.series.map((row) => {
        const point = row as Record<string, unknown>;
        const value = Object.entries(point).find(([key, candidate]) => key !== "period" && typeof candidate === "number")?.[1];
        return { label: String(point.period), value: typeof value === "number" ? value : null };
      })
    : [];
  return (
    <div className="shell section">
      <p className="eyebrow">Consulta pública</p>
      <h1>{item.title}</h1>
      <p className="lede">{item.description}</p>
      {["instituciones", "compras", "contratos", "alertas"].includes(section) && <ExportButton resource={section === "alertas" ? "findings" : "institutions"} />}
      {rows.length > 0 && (
        <DataTable
          headers={Object.keys(rows[0])}
          rows={rows.map((row) => Object.values(row).map(text))}
        />
      )}
      {series.length > 0 && <TimeSeriesChart title={`Evolución de ${item.title}`} data={series} />}
      {summary && series.length === 0 && <pre className="card">{JSON.stringify(summary, null, 2)}</pre>}
      {institutions?.data.length && (
        <div className="grid">
          {institutions.data.map((institution: Institution) => (
            <Link className="card" key={institution.id} href={`/instituciones/${institution.id}`}>
              <strong>{institution.name}</strong><br />Comparar métricas canónicas
            </Link>
          ))}
        </div>
      )}
      {!rows.length && !summary && !institutions?.data.length && <EmptyState title="Sin resultados para los filtros actuales" />}
      <MethodologyNotice />
      <p><Link href="/buscar">Ir al buscador global</Link></p>
    </div>
  );
}
