import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { senators } from "@/lib/legislators";
import { senatorCompletion } from "@/lib/senator-completion";
import { senateCompensation, senateObservationSources, senatorAttendance, senatorInitiatives } from "@/lib/senate-observation";

type PageProps = { params: Promise<{ id: string }> };

function getSenator(id: string) {
  const base = senators.find((item) => item.id === id);
  if (!base) return null;
  return { ...base, ...senatorCompletion[id], photoUrl: base.photoUrl ?? `/api/senator-photo/${base.id}` };
}

function money(value?: number) {
  if (value == null) return "Variable";
  return new Intl.NumberFormat("es-DO", { style: "currency", currency: "DOP", maximumFractionDigits: 0 }).format(value);
}

function statusLabel(status: string) {
  return ({ introduced: "Depositado", committee: "En comisión", approved_senate: "Aprobado por el Senado", approved_congress: "Aprobado por el Congreso", promulgated: "Promulgado / convertido en ley", rejected: "Rechazado", expired: "Perimido", withdrawn: "Retirado", unknown: "Estado por verificar" } as Record<string,string>)[status] ?? status;
}

export function generateStaticParams() { return senators.map((senator) => ({ id: senator.id })); }

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;
  const senator = getSenator(id);
  if (!senator) return { title: "Senador no encontrado" };
  return { title: `${senator.fullName} · Senado`, description: `Expediente público de ${senator.fullName}: formación, remuneración, asistencia e iniciativas legislativas documentadas por el OED.`, alternates: { canonical: `/poder-legislativo/senadores/${senator.id}` } };
}

export default async function SenatorProfilePage({ params }: PageProps) {
  const { id } = await params;
  const senator = getSenator(id);
  if (!senator) notFound();

  const attendance = senatorAttendance[senator.id] ?? [];
  const initiatives = senatorInitiatives[senator.id] ?? [];
  const plenaries = attendance.reduce((sum, item) => sum + (item.plenarySessions ?? 0), 0);
  const attended = attendance.reduce((sum, item) => sum + (item.attended ?? 0), 0);
  const excused = attendance.reduce((sum, item) => sum + (item.excused ?? 0), 0);
  const unjustified = attendance.reduce((sum, item) => sum + (item.unjustifiedAbsences ?? 0), 0);
  const absent = Math.max(plenaries - attended, 0);
  const attendanceRate = plenaries > 0 ? Math.round((attended / plenaries) * 100) : null;
  const absenceRate = plenaries > 0 ? 100 - attendanceRate! : null;
  const mapQuery = encodeURIComponent(`${senator.province}, República Dominicana`);

  return <>
    <section className="hero senator-profile-hero"><div className="shell"><p className="eyebrow">Expediente legislativo · Senado 2024–2028</p><div className="senator-profile-head"><div className="senator-profile-photo">{/* eslint-disable-next-line @next/next/no-img-element */}<img src={senator.photoUrl} alt={senator.fullName} /></div><div><p className="senator-meta"><span className="badge">{senator.province}</span>{senator.party ? <span>{senator.party}</span> : null}</p><h1>{senator.fullName}</h1><p className="lede">Senador/a de la República por {senator.province}. El OED distingue datos verificados, parciales y todavía pendientes de extracción documental.</p><p><Link className="button secondary" href="/poder-legislativo#senadores">← Volver al Senado</Link></p></div></div></div></section>

    <section className="section"><div className="shell profile-two-column"><div><p className="eyebrow">Territorio representado</p><h2>{senator.province}</h2><div className="province-map-card"><iframe title={`Mapa de ${senator.province}`} src={`https://www.google.com/maps?q=${mapQuery}&output=embed`} loading="lazy" referrerPolicy="no-referrer-when-downgrade" /><strong>{senator.province}</strong><span>1 senador representa esta provincia en el Senado.</span></div></div><div><p className="eyebrow">Formación académica</p><h2>Educación</h2>{senator.education.length ? <ul className="profile-list">{senator.education.map((item, index) => <li key={`${senator.id}-edu-${index}`}><strong>{item.credential}</strong>{item.institution ? <span>{item.institution}</span> : null}{item.status === "in_progress" ? <small>En curso</small> : null}<a href={item.sourceUrl} target="_blank" rel="noreferrer">Ver fuente</a></li>)}</ul> : <div className="notice">{senator.educationNote ?? "No se ha localizado formación académica verificable."}</div>}</div></div></section>

    <section className="section profile-muted-section"><div className="shell"><p className="eyebrow">Remuneración y beneficios</p><h2>¿Cuánto recibe un senador?</h2><p className="lede">El OED separa salario, dietas, viáticos, gastos de representación y fondos institucionales para no presentarlos como si todo fuera sueldo.</p><div className="compensation-grid">{senateCompensation.map((item) => <article className="card compensation-card" key={item.label}><span className={`source-status source-${item.status}`}>{item.status === "verified" ? "Verificado" : item.status === "reported" ? "Reportado" : "Requiere verificación 2026"}</span><h3>{item.label}</h3><strong className="metric">{money(item.amount)}</strong><p>{item.unit === "monthly" ? "mensual" : item.unit === "per_session" ? "por sesión" : "monto variable"}</p><p>{item.description}</p><a href={item.sourceUrl} target="_blank" rel="noreferrer">Fuente documental</a></article>)}</div></div></section>

    <section className="section"><div className="shell"><p className="eyebrow">Actividad parlamentaria</p><h2>Asistencia a plenarias</h2>{attendanceRate == null ? <div className="attendance-pending"><strong>Porcentaje pendiente de cálculo documental</strong><span>El Senado publica asistencia por sesión. El OED está consolidando las actas antes de mostrar un porcentaje.</span></div> : <><div className="attendance-score"><div><span className="attendance-number">{attendanceRate}%</span><strong>Asistencia</strong></div><div><span className="absence-number">{absenceRate}%</span><strong>Inasistencia</strong></div></div><div className="attendance-bar" aria-label={`${attendanceRate}% asistencia y ${absenceRate}% inasistencia`}><span className="attendance-bar-present" style={{ width: `${attendanceRate}%` }} /><span className="attendance-bar-absent" style={{ width: `${absenceRate}%` }} /></div><div className="grid attendance-detail"><article className="card"><strong className="metric">{attended}/{plenaries}</strong><span>Sesiones asistidas</span></article><article className="card"><strong className="metric">{absent}</strong><span>Inasistencias</span></article><article className="card"><strong className="metric">{excused}</strong><span>Ausencias justificadas</span></article><article className="card"><strong className="metric">{unjustified}</strong><span>Ausencias no justificadas</span></article></div></>}<p><a className="button" href={senateObservationSources.attendance} target="_blank" rel="noreferrer">Ver actas oficiales de asistencia</a></p></div></section>

    <section className="section profile-muted-section"><div className="shell"><p className="eyebrow">Producción legislativa</p><h2>Proyectos e iniciativas impulsadas</h2><p className="lede">Cada iniciativa tendrá autoría/coautoría, fecha, número, estado legislativo, resultado final y documento original descargable.</p>{initiatives.length ? <div className="initiative-list">{initiatives.map((initiative,index) => <article className="card" key={`${senator.id}-initiative-${index}`}><p className="senator-meta">{initiative.number ? <span className="badge">{initiative.number}</span> : null}<span>{statusLabel(initiative.status)}</span></p><h3>{initiative.title}</h3>{initiative.role ? <p><strong>Participación:</strong> {initiative.role}</p> : null}{initiative.introducedAt ? <p><strong>Depositada:</strong> {initiative.introducedAt}</p> : null}<p className="senator-links">{initiative.documentUrl ? <a href={initiative.documentUrl} target="_blank" rel="noreferrer">Descargar proyecto</a> : null}<a href={initiative.sourceUrl} target="_blank" rel="noreferrer">Ficha oficial</a></p></article>)}</div> : <div className="notice">Aún no se ha importado el expediente individual de iniciativas. Esto no significa que tenga cero proyectos; el OED no mostrará un cero hasta terminar la extracción oficial.</div>}<div className="senator-links profile-actions"><a className="button" href={senateObservationSources.initiatives} target="_blank" rel="noreferrer">Buscar iniciativas oficiales</a><a className="button secondary" href={senateObservationSources.approvedInitiatives} target="_blank" rel="noreferrer">Ver iniciativas aprobadas</a></div></div></section>

    <section className="section"><div className="shell"><p className="eyebrow">Trazabilidad</p><h2>Fuentes principales</h2><div className="grid"><article className="card"><h3>Perfil oficial</h3><a href={senator.officialProfileUrl} target="_blank" rel="noreferrer">Abrir fuente</a></article><article className="card"><h3>Asistencia</h3><a href={senateObservationSources.attendance} target="_blank" rel="noreferrer">Abrir fuente</a></article><article className="card"><h3>Iniciativas</h3><a href={senateObservationSources.initiatives} target="_blank" rel="noreferrer">Abrir fuente</a></article><article className="card"><h3>Datos abiertos</h3><a href={senateObservationSources.openData} target="_blank" rel="noreferrer">Abrir fuente</a></article></div></div></section>
  </>;
}
