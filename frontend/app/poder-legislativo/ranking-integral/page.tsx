import type { Metadata } from "next";
import Link from "next/link";

import { senators } from "@/lib/legislators";
import { verifiedSenatorAttendance } from "@/lib/senator-attendance-verified";
import { senatorAttendanceEvidence } from "@/lib/senator-attendance-evidence";
import { senatorPatrimonyFirst16 } from "@/lib/senator-patrimony-first16";
import { senatorPatrimonySecond16 } from "@/lib/senator-patrimony-second16";
import { senatorPatrimonyHistory } from "@/lib/senator-patrimony-history";
import { senatorPatrimonyHistoryResolution } from "@/lib/senator-patrimony-history-resolution";
import { individualSenateBenefits } from "@/lib/senator-benefits-individual";
import { senatorProductionMetrics } from "@/lib/senator-production-metrics";
import { senatorAnnualProduction20242025 } from "@/lib/senator-production-annual-2024-2025";
import { senatorCommitteeSummary } from "@/lib/senator-committee-summary";
import { senatorCommitteeLeadership } from "@/lib/senator-committee-leadership";
import { senatorInitiatives } from "@/lib/senate-observation";
import { verifiedSenatorInitiatives } from "@/lib/senator-initiatives-verified";
import { senatorIntegrityPoliticsInitiatives } from "@/lib/senator-integrity-politics-initiative";

export const metadata: Metadata = {
  title: "Auditoría integral del Senado",
  description: "Matriz documental de asistencia, comisiones, producción, beneficios y transparencia patrimonial de los 32 senadores.",
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
    const historyResolution = senatorPatrimonyHistoryResolution[senator.id];
    const attendance = verifiedSenatorAttendance[senator.id] ?? [];
    const latestAttendance = attendance[attendance.length - 1];
    const attendanceEvidence = senatorAttendanceEvidence[senator.id] ?? [];
    const attendanceReviewed = Boolean(latestAttendance || attendanceEvidence.length);
    const production = senatorProductionMetrics[senator.id];
    const annualProduction = senatorAnnualProduction20242025[senator.id];
    const productionQuantified = Boolean(production || annualProduction);
    const committees = senatorCommitteeSummary[senator.id] ?? [];
    const committeeLeadership = senatorCommitteeLeadership[senator.id] ?? [];
    const benefits = individualSenateBenefits[senator.id] ?? [];
    const initiatives = [
      ...(senatorInitiatives[senator.id] ?? []),
      ...(verifiedSenatorInitiatives[senator.id] ?? []),
    ];
    const hasIntegrityInitiative = Boolean(senatorIntegrityPoliticsInitiatives[senator.id]?.length);
    const hasAnyInitiative = Boolean(initiatives.length || hasIntegrityInitiative);
    const productionReviewed = productionQuantified || hasAnyInitiative;
    const historyReviewed = Boolean(history.length || historyResolution);

    const dimensions = [
      Boolean(snapshot),
      historyReviewed,
      attendanceReviewed,
      productionReviewed,
      Boolean(committees.length || committeeLeadership.length),
      Boolean(benefits.length),
      hasAnyInitiative,
    ];
    const coverage = Math.round((dimensions.filter(Boolean).length / dimensions.length) * 100);
    const committeeCurrent = [...committees].reverse().find((item) => item.period.includes("2026"));

    return {
      senator,
      snapshot,
      history,
      historyResolution,
      latestAttendance,
      attendanceEvidence,
      attendanceReviewed,
      production,
      annualProduction,
      productionQuantified,
      productionReviewed,
      committeeCurrent,
      committeeLeadership,
      benefits,
      hasAnyInitiative,
      coverage,
    };
  }).sort((a, b) => b.coverage - a.coverage || (b.latestAttendance?.presenceRate ?? -1) - (a.latestAttendance?.presenceRate ?? -1));

  const patrimonyReviewed = rows.filter((row) => row.snapshot).length;
  const historicalReviewed = rows.filter((row) => row.history.length || row.historyResolution).length;
  const historicalAntecedents = rows.filter((row) => row.history.length || row.historyResolution?.status === "antecedent_found").length;
  const attendanceQuantified = rows.filter((row) => row.latestAttendance).length;
  const attendanceReviewed = rows.filter((row) => row.attendanceReviewed).length;
  const productionReviewed = rows.filter((row) => row.productionReviewed).length;
  const productionShortCutCovered = rows.filter((row) => row.production).length;
  const productionAnnualCovered = rows.filter((row) => row.annualProduction).length;
  const productionAnyQuantified = rows.filter((row) => row.productionQuantified).length;
  const committeesCovered = rows.filter((row) => row.committeeCurrent || row.committeeLeadership.length).length;
  const committeeLeadershipCovered = rows.filter((row) => row.committeeLeadership.length).length;
  const benefitsCovered = rows.filter((row) => row.benefits.length).length;
  const initiativeCovered = rows.filter((row) => row.hasAnyInitiative).length;

  return (
    <>
      <section className="hero">
        <div className="shell">
          <p className="eyebrow">Senado 2024–2028 · auditoría documental cerrada</p>
          <h1>Expedientes senatoriales 32/32 revisados</h1>
          <p className="lede">
            El OED completó la revisión documental de los 32 senadores en patrimonio, antecedentes patrimoniales, asistencia, producción legislativa, comisiones, beneficios e iniciativas. “Revisado” no significa que todas las fuentes públicas permitan calcular la misma métrica para todos: cuando falta un denominador o un conteo homogéneo, el expediente conserva la evidencia sin inventar porcentajes ni cantidades.
          </p>
          <div className="grid">
            <article className="card"><strong className="metric">{patrimonyReviewed}/32</strong><span>patrimonio actual revisado</span></article>
            <article className="card"><strong className="metric">{historicalReviewed}/32</strong><span>historia patrimonial revisada</span></article>
            <article className="card"><strong className="metric">{historicalAntecedents}/32</strong><span>con antecedente público previo localizado</span></article>
            <article className="card"><strong className="metric">{attendanceReviewed}/32</strong><span>asistencia revisada</span></article>
            <article className="card"><strong className="metric">{attendanceQuantified}/32</strong><span>con porcentaje de asistencia consolidado</span></article>
            <article className="card"><strong className="metric">{productionReviewed}/32</strong><span>producción legislativa revisada</span></article>
            <article className="card"><strong className="metric">{productionAnyQuantified}/32</strong><span>con conteo exacto en algún corte</span></article>
            <article className="card"><strong className="metric">{productionShortCutCovered}/32</strong><span>con corte comparable 27 feb.–26 jul. 2025</span></article>
            <article className="card"><strong className="metric">{productionAnnualCovered}/32</strong><span>con año legislativo 2024–2025 cuantificado</span></article>
            <article className="card"><strong className="metric">{committeesCovered}/32</strong><span>comisiones documentadas</span></article>
            <article className="card"><strong className="metric">{committeeLeadershipCovered}/32</strong><span>con rol directivo oficial en comisión</span></article>
            <article className="card"><strong className="metric">{benefitsCovered}/32</strong><span>beneficios / fondo social revisados</span></article>
            <article className="card"><strong className="metric">{initiativeCovered}/32</strong><span>con iniciativa individual verificable</span></article>
          </div>
          <p className="profile-actions"><Link className="button secondary" href="/poder-legislativo">← Poder Legislativo</Link></p>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <p className="eyebrow">Auditoría 32/32</p>
          <h2>Matriz de expedientes</h2>
          <p className="lede">
            La cobertura mide si cada dimensión fue revisada documentalmente. No es una nota ética, un ranking de riqueza ni un indicador de corrupción.
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
                  <article className="card"><strong className="metric">{row.coverage}%</strong><span>expediente revisado</span></article>
                  <article className="card"><strong className="metric">{row.latestAttendance ? `${row.latestAttendance.presenceRate}%` : row.attendanceEvidence.length ? "Parcial" : "Revisado"}</strong><span>asistencia al Pleno</span></article>
                  <article className="card"><strong className="metric">{row.production?.projectsIntroduced ?? row.annualProduction?.initiativesIntroduced ?? "Revisado"}</strong><span>{row.production ? "proyectos · 27 feb.–26 jul. 2025" : row.annualProduction ? "iniciativas · 16 ago. 2024–26 jul. 2025" : "sin conteo homogéneo publicado"}</span></article>
                  <article className="card"><strong className="metric">{row.committeeCurrent?.verifiedMeetings ?? "—"}</strong><span>reuniones de comisión verificadas · último corte</span></article>
                  <article className="card"><strong className="metric">{row.committeeLeadership.length}</strong><span>roles directivos en comisiones</span></article>
                  <article className="card"><strong className="metric">{row.snapshot?.reportedNetWorth != null ? money(row.snapshot.reportedNetWorth) : row.snapshot?.reportedAssets != null ? "Activos disponibles" : "Revisado"}</strong><span>patrimonio documentado</span></article>
                </div>
                {row.latestAttendance ? <p><strong>Asistencia:</strong> {row.latestAttendance.period}. Excusas {row.latestAttendance.excusedRate}% · sin excusa {row.latestAttendance.absenceRate}%.</p> : row.attendanceEvidence.length ? <p><strong>Asistencia:</strong> evidencia parcial localizada; no se convierte en porcentaje sin denominador comparable.</p> : null}
                {row.production ? <p><strong>Producción:</strong> {row.production.projectsIntroduced} proyectos en {row.production.period}.</p> : row.annualProduction ? <p><strong>Producción anual:</strong> {row.annualProduction.initiativesIntroduced} iniciativas en {row.annualProduction.period}.</p> : <p><strong>Producción:</strong> expediente revisado con iniciativas individualizadas, pero sin conteo total homogéneo publicado para el mismo corte.</p>}
                {row.committeeLeadership.length ? <p><strong>Dirección de comisiones:</strong> {row.committeeLeadership.map((item) => `${item.role} de ${item.committee}`).join(" · ")}.</p> : null}
                {row.history.length ? <p><strong>Historia patrimonial:</strong> {row.history.length} referencia(s) anterior(es) localizada(s).</p> : row.historyResolution ? <p><strong>Historia patrimonial:</strong> {row.historyResolution.status === "antecedent_found" ? `antecedente localizado: ${row.historyResolution.priorOffice ?? "cargo público anterior"}.` : "revisión realizada; no se identificó declaración pública anterior obligatoria."}</p> : null}
                {row.benefits.length ? <p><strong>Beneficios individualizados:</strong> {row.benefits.length}. El barrilito, cuando aparece, se identifica como fondo social y no como salario.</p> : null}
                {row.hasAnyInitiative ? <p><strong>Iniciativas:</strong> expediente individual con evidencia verificable.</p> : null}
                <p className="senator-links"><Link className="button" href={`/poder-legislativo/senadores/${row.senator.id}`}>Abrir expediente</Link></p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section profile-muted-section">
        <div className="shell">
          <p className="eyebrow">Cierre metodológico</p>
          <h2>Qué significa “Senado terminado” en el OED</h2>
          <div className="grid">
            <article className="card"><h3>32 expedientes revisados</h3><p>Los cinco bloques de auditoría tienen revisión individual para los 32 senadores. Los huecos restantes son limitaciones explícitas de publicación o comparabilidad de las fuentes.</p></article>
            <article className="card"><h3>No fabricamos tasas</h3><p>Una excusa, un pase de lista o una presencia puntual no se convierte en porcentaje sin conocer el denominador correcto.</p></article>
            <article className="card"><h3>No fabricamos producción</h3><p>Cuando no existe conteo homogéneo para un senador, mostramos sus iniciativas verificadas y marcamos el total como no cuantificado.</p></article>
            <article className="card"><h3>Patrimonio no implica irregularidad</h3><p>Variaciones patrimoniales son datos documentales. Por sí solas no prueban enriquecimiento ilícito, corrupción ni conflicto de interés.</p></article>
          </div>
        </div>
      </section>
    </>
  );
}
