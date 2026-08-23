import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { senators } from "@/lib/legislators";
import {
  senateCompensation,
  senateObservationSources,
  senatorAttendance,
  senatorInitiatives,
} from "@/lib/senate-observation";

type PageProps = { params: Promise<{ id: string }> };

function money(value?: number) {
  if (value == null) return "Variable";
  return new Intl.NumberFormat("es-DO", {
    style: "currency",
    currency: "DOP",
    maximumFractionDigits: 0,
  }).format(value);
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    introduced: "Depositado",
    committee: "En comisión",
    approved_senate: "Aprobado por el Senado",
    approved_congress: "Aprobado por el Congreso",
    promulgated: "Promulgado / convertido en ley",
    rejected: "Rechazado",
    expired: "Perimido",
    withdrawn: "Retirado",
    unknown: "Estado por verificar",
  };
  return labels[status] ?? status;
}

export function generateStaticParams() {
  return senators.map((senator) => ({ id: senator.id }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;
  const senator = senators.find((item) => item.id === id);
  if (!senator) return { title: "Senador no encontrado" };
  return {
    title: `${senator.fullName} · Senado`,
    description: `Expediente público del senador ${senator.fullName}, representante de ${senator.province}: formación, remuneración, asistencia e iniciativas legislativas documentadas por el OED.`,
    alternates: { canonical: `/poder-legislativo/senadores/${senator.id}` },
  };
}

export default async function SenatorProfilePage({ params }: PageProps) {
  const { id } = await params;
  const senator = senators.find((item) => item.id === id);
  if (!senator) notFound();

  const attendance = senatorAttendance[senator.id] ?? [];
  const initiatives = senatorInitiatives[senator.id] ?? [];
  const attended = attendance.reduce((sum, item) => sum + (item.attended ?? 0), 0);
  const plenaries = attendance.reduce((sum, item) => sum + (item.plenarySessions ?? 0), 0);
  const attendanceRate = plenaries > 0 ? Math.round((attended / plenaries) * 100) : null;

  const mapQuery = encodeURIComponent(`${senator.province}, República Dominicana`);

  return (
    <>
      <section className="hero senator-profile-hero">
        <div className="shell">
          <p className="eyebrow">Expediente legislativo · Senado 2024–2028</p>
          <div className="senator-profile-head">
            <div className="senator-profile-photo">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={senator.photoUrl ?? `/api/senate-photo/${senator.id}`} alt={senator.fullName} />
            </div>
            <div>
              <p className="senator-meta"><span className="badge">{senator.province}</span>{senator.party ? <span>{senator.party}</span> : null}</p>
              <h1>{senator.fullName}</h1>
              <p className="lede">Senador/a de la República por {senator.province}. Esta ficha separa hechos verificados, datos parciales y campos todavía pendientes de extracción documental.</p>
              <p><Link className="button secondary" href="/poder-legislativo#senadores">← Volver al Senado</Link></p>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="shell profile-two-column">
          <div>
            <p className="eyebrow">Territorio representado</p>
            <h2>{senator.province}</h2>
            <div className="province-map-card">
              <iframe
                title={`Mapa de ${senator.province}`}
                src={`https://www.google.com/maps?q=${mapQuery}&output=embed`}
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
              />
              <strong>{senator.province}</strong>
              <span>1 senador representa esta provincia en el Senado.</span>
            </div>
          </div>

          <div>
            <p className="eyebrow">Formación académica</p>
            <h2>Educación</h2>
            {senator.education.length ? (
              <ul className="profile-list">
                {senator.education.map((item, index) => (
                  <li key={`${senator.id}-edu-${index}`}>
                    <strong>{item.credential}</strong>
                    {item.institution ? <span>{item.institution}</span> : null}
                    {item.status === "in_progress" ? <small>En curso</small> : null}
                    <a href={item.sourceUrl} target="_blank" rel="noreferrer">Ver fuente</a>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="notice">{senator.educationNote ?? "No se ha localizado formación académica verificable en las fuentes consultadas."}</div>
            )}
          </div>
        </div>
      </section>

      <section className="section profile-muted-section">
        <div className="shell">
          <p className="eyebrow">Remuneración y beneficios</p>
          <h2>¿Cuánto recibe un senador?</h2>
          <p className="lede">El OED distingue el salario personal de viáticos, dietas, gastos de representación y fondos institucionales. No se suman como si todo fuera salario.</p>
          <div className="compensation-grid">
            {senateCompensation.map((item) => (
              <article className="card compensation-card" key={item.label}>
                <span className={`source-status source-${item.status}`}>{item.status === "verified" ? "Verificado" : item.status === "reported" ? "Reportado" : "Requiere verificación 2026"}</span>
                <h3>{item.label}</h3>
                <strong className="metric">{money(item.amount)}</strong>
                <p>{item.unit === "monthly" ? "mensual" : item.unit === "per_session" ? "por sesión" : "monto variable"}</p>
                <p>{item.description}</p>
                <a href={item.sourceUrl} target="_blank" rel="noreferrer">Fuente documental</a>
              </article>
            ))}
          </div>
          <div className="notice"><strong>Salario fijo verificado: RD$320,000 mensuales.</strong> Los demás componentes se muestran separados y con su nivel de verificación para evitar confundir remuneración personal con gastos o fondos de representación.</div>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <p className="eyebrow">Actividad parlamentaria</p>
          <h2>Plenarias y asistencia</h2>
          <div className="grid">
            <article className="card"><strong className="metric">{plenaries || "—"}</strong><span>Plenarias medidas en el OED</span></article>
            <article className="card"><strong className="metric">{attended || "—"}</strong><span>Asistencias verificadas</span></article>
            <article className="card"><strong className="metric">{attendanceRate == null ? "—" : `${attendanceRate}%`}</strong><span>Tasa de asistencia</span></article>
          </div>
          {attendance.length === 0 ? (
            <div className="notice">La estructura ya está habilitada. El Senado publica una hoja de asistencia descargable por cada sesión del Pleno; el OED todavía está consolidando esas hojas por senador y no mostrará un porcentaje inventado.</div>
          ) : null}
          <p><a className="button" href={senateObservationSources.attendance} target="_blank" rel="noreferrer">Ver asistencia oficial del Senado</a></p>
        </div>
      </section>

      <section className="section profile-muted-section">
        <div className="shell">
          <p className="eyebrow">Producción legislativa</p>
          <h2>Proyectos e iniciativas impulsadas</h2>
          <p className="lede">Cada iniciativa se clasificará por autoría/coautoría, fecha, número, etapa, resultado y documento original descargable.</p>
          {initiatives.length ? (
            <div className="initiative-list">
              {initiatives.map((initiative, index) => (
                <article className="card" key={`${senator.id}-initiative-${index}`}>
                  <p className="senator-meta">{initiative.number ? <span className="badge">{initiative.number}</span> : null}<span>{statusLabel(initiative.status)}</span></p>
                  <h3>{initiative.title}</h3>
                  {initiative.role ? <p><strong>Participación:</strong> {initiative.role}</p> : null}
                  {initiative.introducedAt ? <p><strong>Depositada:</strong> {initiative.introducedAt}</p> : null}
                  <p className="senator-links">
                    {initiative.documentUrl ? <a href={initiative.documentUrl} target="_blank" rel="noreferrer">Descargar proyecto</a> : null}
                    <a href={initiative.sourceUrl} target="_blank" rel="noreferrer">Ficha oficial</a>
                  </p>
                </article>
              ))}
            </div>
          ) : (
            <div className="notice">Aún no se ha importado al OED el expediente individual de iniciativas de este senador. Esto no significa que tenga cero proyectos. La consulta oficial 2024–2028 está enlazada abajo y será la fuente para poblar esta sección.</div>
          )}
          <div className="senator-links profile-actions">
            <a className="button" href={senateObservationSources.initiatives} target="_blank" rel="noreferrer">Buscar iniciativas oficiales</a>
            <a className="button secondary" href={senateObservationSources.approvedInitiatives} target="_blank" rel="noreferrer">Ver iniciativas aprobadas</a>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <p className="eyebrow">Trazabilidad</p>
          <h2>Fuentes principales</h2>
          <div className="grid">
            <article className="card"><h3>Perfil oficial</h3><p>Biografía, provincia y formación.</p><a href={senator.officialProfileUrl} target="_blank" rel="noreferrer">Abrir fuente</a></article>
            <article className="card"><h3>Asistencia</h3><p>Hojas oficiales por sesión del Pleno.</p><a href={senateObservationSources.attendance} target="_blank" rel="noreferrer">Abrir fuente</a></article>
            <article className="card"><h3>Iniciativas</h3><p>Sistema legislativo del período 2024–2028.</p><a href={senateObservationSources.initiatives} target="_blank" rel="noreferrer">Abrir fuente</a></article>
            <article className="card"><h3>Datos abiertos</h3><p>Sesiones e indicadores legislativos publicados por el Senado.</p><a href={senateObservationSources.openData} target="_blank" rel="noreferrer">Abrir fuente</a></article>
          </div>
        </div>
      </section>
    </>
  );
}
