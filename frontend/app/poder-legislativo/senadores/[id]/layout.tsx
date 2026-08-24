import type { ReactNode } from "react";

import { senators } from "@/lib/legislators";
import { individualSenateBenefits } from "@/lib/senator-benefits-individual";
import { senatorCommitteeLeadership } from "@/lib/senator-committee-leadership";
import { senatorCommitteeSummary } from "@/lib/senator-committee-summary";
import { senatorPatrimonyHistoryResolution } from "@/lib/senator-patrimony-history-resolution";
import { verifiedSenatorInitiatives } from "@/lib/senator-initiatives-verified";

function money(value?: number) {
  if (value == null) return "—";
  return new Intl.NumberFormat("es-DO", {
    style: "currency",
    currency: "DOP",
    maximumFractionDigits: 0,
  }).format(value);
}

function roleLabel(role: "presidente" | "vicepresidente" | "secretario") {
  if (role === "presidente") return "Presidencia";
  if (role === "vicepresidente") return "Vicepresidencia";
  return "Secretaría";
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    introduced: "Depositado",
    committee: "En comisión",
    approved_senate: "Aprobado por el Senado",
    approved_congress: "Aprobado por el Congreso",
    promulgated: "Promulgado / ley",
    rejected: "Rechazado",
    expired: "Perimido",
    withdrawn: "Retirado",
    unknown: "Estado por verificar",
  };
  return labels[status] ?? status;
}

export default async function SenatorEvidenceLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const senator = senators.find((item) => item.id === id);
  const benefits = individualSenateBenefits[id] ?? [];
  const leadership = senatorCommitteeLeadership[id] ?? [];
  const committeePeriods = senatorCommitteeSummary[id] ?? [];
  const initiatives = verifiedSenatorInitiatives[id] ?? [];
  const patrimonyHistoryResolution = senatorPatrimonyHistoryResolution[id];

  return (
    <>
      {children}

      {(benefits.length || leadership.length || committeePeriods.length || initiatives.length || patrimonyHistoryResolution) && senator ? (
        <section className="section profile-muted-section">
          <div className="shell">
            <p className="eyebrow">Expediente complementario verificado</p>
            <h2>Datos individualizados de {senator.fullName}</h2>
            <p className="lede">
              Esta sección contiene evidencia atribuible al senador concreto y evita sustituir datos individuales por promedios generales del Senado.
            </p>

            {patrimonyHistoryResolution ? (
              <>
                <h3 className="research-heading">Antecedente para evolución patrimonial</h3>
                <article className="card">
                  <span className={`source-status source-${patrimonyHistoryResolution.status === "antecedent_found" ? "verified" : "reported"}`}>
                    {patrimonyHistoryResolution.status === "antecedent_found" ? "Antecedente localizado" : "Sin declaración previa identificada"}
                  </span>
                  {patrimonyHistoryResolution.priorOffice ? <h3>{patrimonyHistoryResolution.priorOffice}</h3> : <h3>Revisión de antecedente público</h3>}
                  {patrimonyHistoryResolution.period ? <p><strong>Período:</strong> {patrimonyHistoryResolution.period}</p> : null}
                  <p>{patrimonyHistoryResolution.note}</p>
                  <a href={patrimonyHistoryResolution.sourceUrl} target="_blank" rel="noreferrer">Ver fuente</a>
                </article>
              </>
            ) : null}

            {benefits.length ? (
              <>
                <h3 className="research-heading">Ingresos, asignaciones y fondos individualizados</h3>
                <div className="grid">
                  {benefits.map((item, index) => (
                    <article className="card" key={`${id}-benefit-${index}`}>
                      <span className={`source-status source-${item.status === "verified" ? "verified" : "reported"}`}>
                        {item.status === "verified" ? "Verificado" : item.status === "does_not_receive" ? "No lo recibe" : "Reportado"}
                      </span>
                      <h3>{item.label}</h3>
                      <strong className="metric">
                        {item.status === "does_not_receive" ? "No recibe" : item.monthlyAmount != null ? money(item.monthlyAmount) : "Documentado"}
                      </strong>
                      {item.monthlyAmount != null ? <p>Mensual</p> : null}
                      <p>{item.kind === "social_fund" ? "Fondo institucional/social; no es salario personal." : "Ingreso o asignación individual documentada."}</p>
                      {item.note ? <p>{item.note}</p> : null}
                      <a href={item.sourceUrl} target="_blank" rel="noreferrer">Ver fuente</a>
                    </article>
                  ))}
                </div>
              </>
            ) : null}

            {leadership.length || committeePeriods.length ? (
              <>
                <h3 className="research-heading">Actividad y responsabilidad en comisiones</h3>
                {leadership.length ? (
                  <div className="grid">
                    {leadership.map((item, index) => (
                      <article className="card" key={`${id}-committee-role-${index}`}>
                        <span className="badge">{roleLabel(item.role)}</span>
                        <h3>{item.committee}</h3>
                        <p>{item.period}</p>
                        <a href={item.sourceUrl} target="_blank" rel="noreferrer">Listado oficial de comisiones</a>
                      </article>
                    ))}
                  </div>
                ) : null}
                {committeePeriods.map((period, index) => (
                  <article className="card" key={`${id}-committee-period-${index}`}>
                    <h3>{period.period}</h3>
                    {period.verifiedMeetings != null ? <p><strong>Reuniones individualmente verificadas:</strong> {period.verifiedMeetings}</p> : null}
                    {period.verifiedMinutes != null ? <p><strong>Minutos de presencia verificados:</strong> {period.verifiedMinutes}</p> : null}
                    {period.attendanceRate != null ? <p><strong>Asistencia publicada:</strong> {period.attendanceRate}%</p> : null}
                    <p>{period.note}</p>
                    <a href={period.sourceUrl} target="_blank" rel="noreferrer">Ver fuente</a>
                  </article>
                ))}
              </>
            ) : null}

            {initiatives.length ? (
              <>
                <h3 className="research-heading">Iniciativas adicionales verificadas</h3>
                <div className="initiative-list">
                  {initiatives.map((initiative, index) => (
                    <article className="card" key={`${id}-verified-initiative-${index}`}>
                      <p className="senator-meta">
                        {initiative.number ? <span className="badge">{initiative.number}</span> : null}
                        <span>{statusLabel(initiative.status)}</span>
                      </p>
                      <h3>{initiative.title}</h3>
                      {initiative.role ? <p><strong>Participación:</strong> {initiative.role}</p> : null}
                      {initiative.introducedAt ? <p><strong>Fecha:</strong> {initiative.introducedAt}</p> : null}
                      <a href={initiative.sourceUrl} target="_blank" rel="noreferrer">Ver fuente</a>
                    </article>
                  ))}
                </div>
              </>
            ) : null}
          </div>
        </section>
      ) : null}
    </>
  );
}
