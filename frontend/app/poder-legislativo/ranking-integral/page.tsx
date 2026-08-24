import type { Metadata } from "next";
import Link from "next/link";

import { senators } from "@/lib/legislators";
import { verifiedSenatorAttendance } from "@/lib/senator-attendance-verified";
import { senatorPatrimonyFirst16 } from "@/lib/senator-patrimony-first16";
import { senatorPatrimonySecond16 } from "@/lib/senator-patrimony-second16";
import { senatorPatrimonyHistory } from "@/lib/senator-patrimony-history";
import { individualSenateBenefits } from "@/lib/senator-benefits-individual";
import { senatorProductionMetrics } from "@/lib/senator-production-metrics";
import { senatorCommitteeSummary } from "@/lib/senator-committee-summary";
import { senatorCommitteeLeadership } from "@/lib/senator-committee-leadership";
import { senatorInitiatives } from "@/lib/senate-observation";
import { verifiedSenatorInitiatives } from "@/lib/senator-initiatives-verified";
import { senatorIntegrityPoliticsInitiatives } from "@/lib/senator-integrity-politics-initiative";

export const metadata: Metadata = {
  title: "Ranking integral del Senado",
  description: "Matriz comparativa de asistencia, comisiones, producción, beneficios y transparencia patrimonial de los 32 senadores.",
  alternates: { canonical: "/poder-legislativo/ranking-integral" },
};

function money(value?: number) {
  if (value == null) return "—";
  return new Intl.NumberFormat("es-DO", { style: "currency", currency: "DOP", maximumFractionDigits: 0 }).format(value);
}

export default function IntegralSenateRankingPage() {
  const rows = senators.map((senator) => {
    const snapshot = senatorPatrimonyFirst16[senator.id] ?? senatorPatrimonySecond16[senator.id];
    const history = senatorPatrimonyHistory[senator.id] ?? [];
    const attendance = verifiedSenatorAttendance[senator.id] ?? [];
    const latestAttendance = attendance[attendance.length - 1];
    const production = senatorProductionMetrics[senator.id];
    const committees = senatorCommitteeSummary[senator.id] ?? [];
    const committeeLeadership = senatorCommitteeLeadership[senator.id] ?? [];
    const benefits = individualSenateBenefits[senator.id] ?? [];
    const initiatives = [
      ...(senatorInitiatives[senator.id] ?? []),
      ...(verifiedSenatorInitiatives[senator.id] ?? []),
      ...(senatorIntegrityPoliticsInitiatives[senator.id] ?? []),
    ];

    const dimensions = [
      Boolean(snapshot),
      Boolean(history.length),
      Boolean(latestAttendance),
      Boolean(production),
      Boolean(committees.length || committeeLeadership.length),
      Boolean(benefits.length),
      Boolean(initiatives.length),
    ];
    const coverage = Math.round((dimensions.filter(Boolean).length / dimensions.length) * 100);
    const committeeCurrent = [...committees].reverse().find((item) => item.period.includes("2026"));

    return {
      senator,
      snapshot,
      history,
      latestAttendance,
      production,
      committeeCurrent,
      committeeLeadership,
      benefits,
      initiatives,
      coverage,
    };
  }).sort((a, b) => b.coverage - a.coverage || (b.latestAttendance?.presenceRate ?? -1) - (a.latestAttendance?.presenceRate ?? -1));

  const fullPatrimony = rows.filter((row) => row.snapshot?.reportedNetWorth != null).length;
  const historical = rows.filter((row) => row.history.length).length;
  const attendanceCovered = rows.filter((row) => row.latestAttendance).length;
  const productionCovered = rows.filter((row) => row.production).length;
  const committeesCovered = rows.filter((row) => row.committeeCurrent || row.committeeLeadership.length).length;
  const committeeLeadershipCovered = rows.filter((row) => row.committeeLeadership.length).length;
  const benefitsCovered = rows.filter((row) => row.benefits.length).length;
  const initiativesCovered = rows.filter((row) => row.initiatives.length).length;

  return (
    <>
      <section className="hero">
        <div className="shell">
          <p className="eyebrow">Senado 2024–2028 · control de calidad</p>
          <h1>Ranking integral y cobertura de expedientes</h1>
          <p className="lede">
            Esta primera versión ordena por completitud documental, no por riqueza ni por una presunción de desempeño. Las métricas de actividad se muestran con su período original y solo se comparan directamente cuando usan un corte compatible.
          </p>
          <div className="grid">
            <article className="card"><strong className="metric">{attendanceCovered}/32</strong><span>con asistencia cuantificada</span></article>
            <article className="card"><strong className="metric">{productionCovered}/32</strong><span>con producción comparable 2025</span></article>
            <article className="card"><strong className="metric">{committeesCovered}/32</strong><span>con actividad o rol de comisión documentado</span></article>
            <article className="card"><strong className="metric">{committeeLeadershipCovered}/32</strong><span>con cargo directivo en comisión permanente</span></article>
            <article className="card"><strong className="metric">{fullPatrimony}/32</strong><span>con patrimonio neto cuantificado</span></article>
            <article className="card"><strong className="metric">{historical}/32</strong><span>con historia patrimonial</span></article>
            <article className="card"><strong className="metric">{benefitsCovered}/32</strong><span>con beneficios individualizados</span></article>
            <article className="card"><strong className="metric">{initiativesCovered}/32</strong><span>con al menos una iniciativa individual documentada</span></article>
          </div>
          <p className="profile-actions"><Link className="button secondary" href="/poder-legislativo">← Poder Legislativo</Link></p>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <p className="eyebrow">Auditoría 32/32</p>
          <h2>Matriz comparativa</h2>
          <p className="lede">
            Cobertura = presencia de evidencia en siete dimensiones: patrimonio actual, historia patrimonial, asistencia al Pleno, producción comparable, comisiones, beneficios individuales e iniciativas verificadas. No es una nota de calidad ética ni de corrupción.
          </p>
          <div className="initiative-list">
            {rows.map((row, index) => (
              <article className="card" key={row.senator.id}>
                <p className="senator-meta">
                  <span className="badge">#{index + 1} cobertura</span>
                  <span>{row.senator.province}</span>
                  {row.senator.party ? <span>{row.senator.party}</span> : null}
                </p>
                <h3>{row.senator.fullName}</h3>
                <div className="grid attendance-detail">
                  <article className="card"><strong className="metric">{row.coverage}%</strong><span>expediente observable</span></article>
                  <article className="card"><strong className="metric">{row.latestAttendance ? `${row.latestAttendance.presenceRate}%` : "—"}</strong><span>presencia Pleno</span></article>
                  <article className="card"><strong className="metric">{row.production?.projectsIntroduced ?? "—"}</strong><span>proyectos · 27 feb.–26 jul. 2025</span></article>
                  <article className="card"><strong className="metric">{row.committeeCurrent?.verifiedMeetings ?? "—"}</strong><span>reuniones de comisión verificadas · último corte 2026</span></article>
                  <article className="card"><strong className="metric">{row.committeeCurrent?.verifiedMinutes ?? "—"}</strong><span>minutos verificados en comisión</span></article>
                  <article className="card"><strong className="metric">{row.committeeLeadership.length || "—"}</strong><span>roles directivos en comisiones · ago. 2024–ago. 2026</span></article>
                  <article className="card"><strong className="metric">{row.snapshot?.reportedNetWorth != null ? money(row.snapshot.reportedNetWorth) : row.snapshot?.reportedAssets != null ? "Activos disponibles" : "—"}</strong><span>patrimonio documentado</span></article>
                </div>
                {row.latestAttendance ? <p><strong>Asistencia:</strong> {row.latestAttendance.period}. Excusas {row.latestAttendance.excusedRate}% · sin excusa {row.latestAttendance.absenceRate}%.</p> : null}
                {row.production ? <p><strong>Producción:</strong> {row.production.projectsIntroduced} proyectos en {row.production.period}.</p> : null}
                {row.committeeLeadership.length ? <p><strong>Dirección de comisiones:</strong> {row.committeeLeadership.map((item) => `${item.role} de ${item.committee}`).join(" · ")}.</p> : null}
                {row.history.length ? <p><strong>Historia patrimonial:</strong> {row.history.length} referencia(s) anterior(es) localizada(s).</p> : null}
                {row.benefits.length ? <p><strong>Beneficios individualizados:</strong> {row.benefits.length}. El barrilito, cuando aparece, se identifica como fondo social y no como salario.</p> : null}
                {row.initiatives.length ? <p><strong>Iniciativas con ficha individual:</strong> {row.initiatives.length} registro(s) ya enlazado(s).</p> : null}
                <p className="senator-links"><Link className="button" href={`/poder-legislativo/senadores/${row.senator.id}`}>Abrir expediente</Link></p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section profile-muted-section">
        <div className="shell">
          <p className="eyebrow">Regla metodológica</p>
          <h2>Lo que todavía no mezclamos</h2>
          <div className="grid">
            <article className="card"><h3>Patrimonio no puntúa desempeño</h3><p>Tener más, menos o aumentar patrimonio no produce una nota positiva o negativa. Solo medimos disponibilidad y trazabilidad documental.</p></article>
            <article className="card"><h3>Comisiones requieren denominador</h3><p>Los minutos y reuniones verificadas se muestran, pero no se convierten en porcentaje hasta conocer todas las convocatorias que correspondían a cada senador en el mismo período.</p></article>
            <article className="card"><h3>Períodos separados</h3><p>Producción 2025, asistencia 2026 y datos históricos se etiquetan por separado. Un futuro índice de desempeño solo combinará cortes temporalmente compatibles.</p></article>
          </div>
        </div>
      </section>
    </>
  );
}
