import Link from "next/link";
import {
  Breadcrumbs,
  DataTable,
  EmptyState,
  FreshnessIndicator,
  MethodologyNotice,
  MetricCard,
  StatusBadge,
} from "@/components/ui";
import { api, getInstitutionProfile, getInstitutionSection, optional } from "@/lib/api";
import type { Collection } from "@/types/public";

const sections = [
  ["structure", "Estructura"],
  ["positions", "Cargos"],
  ["employment", "Empleo"],
  ["payroll", "Nómina"],
  ["budget", "Presupuesto"],
  ["procurement", "Compras"],
  ["debt", "Deuda"],
  ["assets", "Patrimonio"],
  ["findings", "Alertas"],
  ["sources", "Fuentes"],
  ["history", "Historial"],
] as const;

function display(value: unknown) {
  if (value === null || value === undefined) return "No disponible";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export default async function Profile({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const profile = await optional(getInstitutionProfile(id));
  if (!profile) return <div className="shell section"><EmptyState title="Institución no disponible" /></div>;
  const loaded = await Promise.all(
    sections.map(async ([key, label]) => [
      key,
      label,
      key === "findings"
        ? await optional(api<Collection<Record<string, unknown>>>(`/institutions/${encodeURIComponent(id)}/findings`))
        : await optional(getInstitutionSection(id, key)),
    ] as const),
  );
  return (
    <div className="shell section">
      <Breadcrumbs items={[{ href: "/", label: "Inicio" }, { href: "/instituciones", label: "Instituciones" }]} />
      <p className="eyebrow">Perfil institucional</p>
      <h1>{profile.data.name}</h1>
      <p><StatusBadge>{profile.data.data_quality}</StatusBadge> · <FreshnessIndicator value={profile.data.last_updated ?? "No disponible"} /></p>
      <nav className="tabs" aria-label="Secciones del perfil">
        {loaded.map(([key, label]) => <Link key={key} href={`#${key}`}>{label}</Link>)}
      </nav>
      <section id="summary">
        <h2>Resumen</h2>
        <div className="grid">
          {Object.entries(profile.data.metrics).map(([key, value]) => (
            <MetricCard key={key} label={key} value={value} note={profile.data.coverage[key]} />
          ))}
        </div>
        <p>Base legal: {profile.data.legal_basis?.title ?? "No disponible"}</p>
      </section>
      {loaded.map(([key, label, result]) => (
        <section id={key} key={key}>
          <h2>{label}</h2>
          {result?.data.length ? (
            <DataTable
              headers={Object.keys(result.data[0])}
              rows={result.data.map((row) => Object.values(row).map(display))}
            />
          ) : <EmptyState title={`Datos de ${label.toLowerCase()} no disponibles`} />}
        </section>
      ))}
      <MethodologyNotice />
    </div>
  );
}
