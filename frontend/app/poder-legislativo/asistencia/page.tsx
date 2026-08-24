import type { Metadata } from "next";
import Link from "next/link";

import { senators } from "@/lib/legislators";
import { verifiedSenatorAttendance } from "@/lib/senator-attendance-verified";
import { senatorAttendanceEvidence } from "@/lib/senator-attendance-evidence";
import { verifiedSenatorCommissionAttendance } from "@/lib/senator-commission-attendance-verified";

export const metadata: Metadata = {
  title: "Ranking de asistencia del Senado",
  description: "Ranking comparativo de asistencia al Pleno y actividad en comisiones de los 32 senadores de la República Dominicana.",
  alternates: { canonical: "/poder-legislativo/asistencia" },
};

const COMMON_PERIOD = "27 feb. – 26 jul. 2026";
const COMMON_SESSIONS = 26;

function latestComparable(id: string) {
  const rows = verifiedSenatorAttendance[id] ?? [];
  return rows.find((row) => row.period === COMMON_PERIOD);
}

function latestDocumented(id: string) {
  const rows = verifiedSenatorAttendance[id] ?? [];
  return rows[rows.length - 1];
}

function commissionSummary(id: string) {
  const rows = verifiedSenatorCommissionAttendance[id] ?? [];
  const present = rows.filter((row) => row.status === "present").length;
  const excused = rows.filter((row) => row.status === "excused").length;
  const absent = rows.filter((row) => row.status === "absent").length;
  const minutes = rows.reduce((sum, row) => sum + (row.durationMinutes ?? 0), 0);
  return { rows, present, excused, absent, minutes };
}

export default function SenateAttendancePage() {
  const ranking = senators
    .map((senator) => {
      const comparable = latestComparable(senator.id);
      const latest = latestDocumented(senator.id);
      const evidence = senatorAttendanceEvidence[senator.id] ?? [];
      const commissions = commissionSummary(senator.id);
      return { senator, comparable, latest, evidence, commissions };
    })
    .sort((a, b) => {
      if (a.comparable && b.comparable) return b.comparable.presenceRate - a.comparable.presenceRate;
      if (a.comparable) return -1;
      if (b.comparable) return 1;
      if (a.latest && b.latest) return b.latest.presenceRate - a.latest.presenceRate;
      if (a.latest) return -1;
      if (b.latest) return 1;
      return a.senator.fullName.localeCompare(b.senator.fullName, "es");
    });

  const exactCommon = ranking.filter((item) => item.comparable).length;
  const withAnyPlenary = ranking.filter((item) => item.latest).length;
  const reviewedPlenary = ranking.filter((item) => item.latest || item.evidence.length).length;
  const withCommission = ranking.filter((item) => item.commissions.rows.length).length;

  return (
    <>
      <section className="hero">
        <div className="shell">
          <p className="eyebrow">Control parlamentario · Senado</p>
          <h1>Ranking de asistencia</h1>
          <p className="lede">
            Comparación de presencia, excusas y ausencias de los 32 senadores. El corte común principal abarca
            <strong> del 27 de febrero al 26 de julio de 2026</strong>, con <strong>26 sesiones del Pleno</strong>.
          </p>
          <p>
            La fuente consolidada del corte común publica conteos individuales completos para 10 senadores. Para los demás,
            el OED muestra el último porcentaje cuantificado disponible cuando existe, indicando expresamente su período; las evidencias parciales no se convierten en porcentajes.
          </p>
          <p><Link className="button secondary" href="/poder-legislativo">← Volver al Poder Legislativo</Link></p>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <div className="grid">
            <article className="card"><span className="eyebrow">Corte comparable</span><strong className="metric">{exactCommon}/32</strong><p>Con porcentaje exacto para las mismas 26 sesiones.</p></article>
            <article className="card"><span className="eyebrow">Asistencia cuantificada</span><strong className="metric">{withAnyPlenary}/32</strong><p>Con al menos un período de asistencia expresado en porcentaje.</p></article>
            <article className="card"><span className="eyebrow">Asistencia revisada</span><strong className="metric">{reviewedPlenary}/32</strong><p>Con porcentaje o evidencia parcial individual documentada.</p></article>
            <article className="card"><span className="eyebrow">Comisiones</span><strong className="metric">{withCommission}/32</strong><p>Con registros individualizados de reuniones ya extraídos.</p></article>
          </div>
        </div>
      </section>

      <section className="section profile-muted-section">
        <div className="shell">
          <p className="eyebrow">Corte común + último dato disponible</p>
          <h2>{COMMON_PERIOD} · {COMMON_SESSIONS} sesiones</h2>
          <p className="lede">
            Los primeros registros con etiqueta <strong>Exacto · corte común</strong> sí son comparables entre sí. Cuando un senador no tiene el mismo corte, mostramos su último porcentaje cuantificado con el período correspondiente; esos registros sirven para conocer su expediente, pero no para ordenarlo contra el corte común.
          </p>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={{ textAlign: "left", padding: "12px" }}>#</th>
                  <th style={{ textAlign: "left", padding: "12px" }}>Senador</th>
                  <th style={{ textAlign: "left", padding: "12px" }}>Provincia</th>
                  <th style={{ textAlign: "right", padding: "12px" }}>Presencia</th>
                  <th style={{ textAlign: "right", padding: "12px" }}>Excusas</th>
                  <th style={{ textAlign: "right", padding: "12px" }}>Sin excusa</th>
                  <th style={{ textAlign: "left", padding: "12px" }}>Período / cobertura</th>
                </tr>
              </thead>
              <tbody>
                {ranking.map((item, index) => {
                  const displayed = item.comparable ?? item.latest;
                  return (
                    <tr key={item.senator.id} style={{ borderTop: "1px solid var(--border, #ddd)" }}>
                      <td style={{ padding: "12px" }}>{index + 1}</td>
                      <td style={{ padding: "12px" }}><Link href={`/poder-legislativo/senadores/${item.senator.id}`}><strong>{item.senator.fullName}</strong></Link></td>
                      <td style={{ padding: "12px" }}>{item.senator.province}</td>
                      <td style={{ textAlign: "right", padding: "12px" }}>{displayed ? `${displayed.presenceRate}%` : "—"}</td>
                      <td style={{ textAlign: "right", padding: "12px" }}>{displayed ? `${displayed.excusedRate}%` : "—"}</td>
                      <td style={{ textAlign: "right", padding: "12px" }}>{displayed ? `${displayed.absenceRate}%` : "—"}</td>
                      <td style={{ padding: "12px" }}>
                        {item.comparable
                          ? "Exacto · corte común"
                          : item.latest
                            ? `Otro corte · ${item.latest.period}`
                            : item.evidence.length
                              ? `Evidencia parcial · ${item.evidence[0].metric}: ${item.evidence[0].value}`
                              : "Revisión sin porcentaje comparable"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p><small>Nota: una cifra de otro período no se utiliza para establecer el ranking del corte común de 2026. Su función es evitar que un expediente ya cuantificado aparezca falsamente como vacío.</small></p>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <p className="eyebrow">Actividad en comisiones</p>
          <h2>Reuniones verificadas</h2>
          <p className="lede">
            Aquí se muestran únicamente registros individualizados ya extraídos de los informes mensuales del Senado. Incluyen fecha,
            comisión, condición de asistencia y, cuando el documento lo publica, hora de llegada, salida y minutos presentes.
          </p>
          <div className="grid">
            {ranking.filter((item) => item.commissions.rows.length).map((item) => (
              <article className="card" key={`commission-${item.senator.id}`}>
                <p className="senator-meta"><span className="badge">{item.senator.province}</span></p>
                <h3><Link href={`/poder-legislativo/senadores/${item.senator.id}`}>{item.senator.fullName}</Link></h3>
                <p><strong>{item.commissions.present}</strong> presencias verificadas · <strong>{item.commissions.minutes}</strong> minutos registrados</p>
                <ul className="profile-list">
                  {item.commissions.rows.map((row, i) => (
                    <li key={`${item.senator.id}-commission-${i}`}>
                      <strong>{row.date} · {row.commission}</strong>
                      <span>{row.status === "present" ? "Presente" : row.status === "excused" ? "Excusa" : row.status === "absent" ? "Ausente" : "Otra comisión"}</span>
                      {row.arrival || row.departure ? <small>{row.arrival ?? "—"}–{row.departure ?? "—"}{row.durationMinutes != null ? ` · ${row.durationMinutes} min` : ""}</small> : null}
                      <a href={row.sourceUrl} target="_blank" rel="noreferrer">Fuente oficial</a>
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section profile-muted-section">
        <div className="shell">
          <p className="eyebrow">Metodología</p>
          <h2>Cómo leer el ranking</h2>
          <div className="grid">
            <article className="card"><h3>Presencia</h3><p>Sesiones a las que el senador figura asistente dentro del período medido.</p></article>
            <article className="card"><h3>Excusa</h3><p>Inasistencia acompañada de justificación escrita registrada por el Senado. No equivale a ausencia injustificada.</p></article>
            <article className="card"><h3>Ausencia sin excusa</h3><p>Solo se publica cuando el acta la clasifica expresamente así. En el corte de 26 sesiones de 2026, la revisión encontró cero ausencias injustificadas.</p></article>
            <article className="card"><h3>Permanencia</h3><p>Se tratará aparte cuando los dos pases de lista o las horas de entrada y salida permitan medir si el legislador permaneció durante la sesión.</p></article>
          </div>
          <p><a href="https://www.diariolibre.com/politica/congreso-nacional/2026/08/12/los-senadores-se-escudaron-en-100-excusas-para-faltar-a-las-sesiones/3626113" target="_blank" rel="noreferrer">Fuente del corte común de 26 sesiones</a></p>
        </div>
      </section>
    </>
  );
}
