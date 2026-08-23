import type { Metadata } from "next";
import Link from "next/link";

import { senators } from "@/lib/legislators";
import { senatorPatrimonyFirst16 } from "@/lib/senator-patrimony-first16";
import { senatorPatrimonySecond16 } from "@/lib/senator-patrimony-second16";
import { senatorPatrimonyHistory } from "@/lib/senator-patrimony-history";

export const metadata: Metadata = {
  title: "Evolución patrimonial de senadores",
  description:
    "Historial de declaraciones juradas y evolución patrimonial documentada de los 32 senadores de la República Dominicana.",
  alternates: { canonical: "/poder-legislativo/patrimonio/evolucion" },
};

function money(value?: number) {
  if (value == null) return "—";
  return new Intl.NumberFormat("es-DO", {
    style: "currency",
    currency: "DOP",
    maximumFractionDigits: 0,
  }).format(value);
}

function percentage(value: number) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(1)}%`;
}

export default function SenatePatrimonyEvolutionPage() {
  const current = { ...senatorPatrimonyFirst16, ...senatorPatrimonySecond16 };

  const rows = senators.map((senator) => {
    const snapshot = current[senator.id];
    const history = senatorPatrimonyHistory[senator.id] ?? [];
    const earliestComparableNet = history.find((point) => point.comparability === "comparable" && point.reportedNetWorth != null);
    const latestNet = snapshot?.reportedNetWorth;
    const netChange = earliestComparableNet?.reportedNetWorth != null && latestNet != null
      ? latestNet - earliestComparableNet.reportedNetWorth
      : undefined;
    const netChangeRate = netChange != null && earliestComparableNet?.reportedNetWorth
      ? (netChange / earliestComparableNet.reportedNetWorth) * 100
      : undefined;
    return { senator, snapshot, history, earliestComparableNet, netChange, netChangeRate };
  });

  const withHistory = rows.filter((row) => row.history.length > 0).length;
  const withComparableEvolution = rows.filter((row) => row.netChange != null).length;
  const withCurrentNet = rows.filter((row) => row.snapshot?.reportedNetWorth != null).length;

  return (
    <>
      <section className="hero">
        <div className="shell">
          <p className="eyebrow">Declaraciones juradas · serie histórica</p>
          <h1>Evolución patrimonial de los 32 senadores</h1>
          <p className="lede">
            El OED conecta declaraciones anteriores con el corte 2024. Se incluyen cargos previos cuando generaron obligación de declarar. Solo calculamos variación porcentual cuando los puntos pueden compararse con una semántica compatible; un aumento patrimonial no implica por sí solo irregularidad.
          </p>
          <div className="grid">
            <article className="card"><strong className="metric">32</strong><span>senadores revisados</span></article>
            <article className="card"><strong className="metric">{withHistory}</strong><span>con historial previo ya localizado</span></article>
            <article className="card"><strong className="metric">{withCurrentNet}</strong><span>con patrimonio neto 2024 cuantificado</span></article>
            <article className="card"><strong className="metric">{withComparableEvolution}</strong><span>con evolución neta comparable ya calculable</span></article>
          </div>
          <p className="senator-links profile-actions">
            <Link className="button secondary" href="/poder-legislativo/patrimonio">← Ranking patrimonial 2024</Link>
            <Link className="button secondary" href="/poder-legislativo">Poder Legislativo</Link>
          </p>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <p className="eyebrow">Comparación histórica</p>
          <h2>Primera declaración localizada → 2024</h2>
          <p className="lede">
            “Comparable” significa que podemos interpretar el punto histórico como patrimonio neto o como activos/pasivos con suficiente claridad. Los registros parciales siguen visibles, pero no generan un porcentaje automático.
          </p>
          <div className="initiative-list">
            {rows.map(({ senator, snapshot, history, earliestComparableNet, netChange, netChangeRate }) => (
              <article className="card" key={senator.id}>
                <p className="senator-meta">
                  <span className="badge">{senator.province}</span>
                  {senator.party ? <span>{senator.party}</span> : null}
                </p>
                <h3>{senator.fullName}</h3>

                <div className="grid attendance-detail">
                  <article className="card">
                    <strong className="metric">{earliestComparableNet ? money(earliestComparableNet.reportedNetWorth) : "—"}</strong>
                    <span>Primer patrimonio neto comparable</span>
                  </article>
                  <article className="card">
                    <strong className="metric">{money(snapshot?.reportedNetWorth)}</strong>
                    <span>Patrimonio neto 2024</span>
                  </article>
                  <article className="card">
                    <strong className="metric">{netChange != null ? money(netChange) : "—"}</strong>
                    <span>Variación neta documentable</span>
                  </article>
                  <article className="card">
                    <strong className="metric">{netChangeRate != null ? percentage(netChangeRate) : "—"}</strong>
                    <span>Variación porcentual comparable</span>
                  </article>
                </div>

                {history.length ? (
                  <div className="declaration-timeline">
                    {history.map((point, index) => (
                      <article className="card" key={`${senator.id}-${point.date}-${index}`}>
                        <p className="senator-meta">
                          <span className="badge">{point.date}</span>
                          <span>{point.comparability === "comparable" ? "Comparable" : point.comparability === "partial" ? "Referencia parcial" : "Registro histórico"}</span>
                        </p>
                        {point.office ? <h4>{point.office}</h4> : null}
                        {point.reportedAssets != null ? <p><strong>Activos:</strong> {money(point.reportedAssets)}</p> : null}
                        {point.reportedLiabilities != null ? <p><strong>Pasivos:</strong> {money(point.reportedLiabilities)}</p> : null}
                        {point.reportedNetWorth != null ? <p><strong>Patrimonio neto:</strong> {money(point.reportedNetWorth)}</p> : null}
                        {point.reportedAmount != null ? <p><strong>{point.reportedAmountLabel ?? "Monto publicado"}:</strong> {money(point.reportedAmount)}</p> : null}
                        {point.note ? <p>{point.note}</p> : null}
                        <a href={point.sourceUrl} target="_blank" rel="noreferrer">Fuente histórica</a>
                      </article>
                    ))}
                    {snapshot ? (
                      <article className="card">
                        <p className="senator-meta"><span className="badge">{snapshot.declarationPeriod}</span><span>Corte vigente</span></p>
                        <h4>Declaración del período 2024–2028</h4>
                        {snapshot.reportedAssets != null ? <p><strong>Activos/total publicado:</strong> {money(snapshot.reportedAssets)}</p> : null}
                        {snapshot.reportedLiabilities != null ? <p><strong>Pasivos:</strong> {money(snapshot.reportedLiabilities)}</p> : null}
                        {snapshot.reportedNetWorth != null ? <p><strong>Patrimonio neto:</strong> {money(snapshot.reportedNetWorth)}</p> : null}
                        {snapshot.priorDeclarationId ? <p><strong>ID de declaración anterior:</strong> {snapshot.priorDeclarationId}</p> : null}
                        {snapshot.note ? <p>{snapshot.note}</p> : null}
                        <a href={snapshot.declarationUrl} target="_blank" rel="noreferrer">Ver declaración / portal oficial</a>
                      </article>
                    ) : null}
                  </div>
                ) : (
                  <div className="notice">
                    No se ha localizado todavía un monto patrimonial anterior verificable. Esto no significa que el senador nunca haya presentado una declaración; significa que el OED aún no ha resuelto una serie histórica cuantificable.
                  </div>
                )}

                <p className="senator-links profile-actions">
                  <Link href={`/poder-legislativo/senadores/${senator.id}`}>Expediente completo</Link>
                  {snapshot ? <a href={snapshot.declarationUrl} target="_blank" rel="noreferrer">Declaración vigente</a> : null}
                </p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section profile-muted-section">
        <div className="shell">
          <p className="eyebrow">Lectura responsable</p>
          <h2>Qué significa —y qué no significa— la evolución</h2>
          <div className="grid">
            <article className="card"><h3>No mezclar activos y patrimonio neto</h3><p>Cuando una fuente antigua solo dice “bienes” o “patrimonio” pero también enumera deudas, el OED conserva el valor como referencia parcial y no fabrica un neto.</p></article>
            <article className="card"><h3>Monedas y tasas</h3><p>Los montos en dólares se mantienen separados salvo que la fuente documente expresamente la tasa utilizada. La comparación histórica debe conservar la metodología del punto original.</p></article>
            <article className="card"><h3>Variación no es acusación</h3><p>Un aumento patrimonial puede tener múltiples explicaciones lícitas. El OED muestra declaraciones y diferencias documentales; cualquier evaluación de legalidad requiere evidencia adicional.</p></article>
          </div>
        </div>
      </section>
    </>
  );
}
