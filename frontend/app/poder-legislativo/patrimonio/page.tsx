import type { Metadata } from "next";
import Link from "next/link";

import { senators } from "@/lib/legislators";
import { senatorPatrimonyFirst16 } from "@/lib/senator-patrimony-first16";
import { senatorPatrimonySecond16 } from "@/lib/senator-patrimony-second16";

export const metadata: Metadata = {
  title: "Patrimonio de senadores",
  description:
    "Declaraciones juradas, activos, pasivos y patrimonio neto documentado de los 32 senadores de la República Dominicana.",
  alternates: { canonical: "/poder-legislativo/patrimonio" },
};

function money(value?: number) {
  if (value == null) return "Pendiente";
  return new Intl.NumberFormat("es-DO", {
    style: "currency",
    currency: "DOP",
    maximumFractionDigits: 0,
  }).format(value);
}

export default function SenatePatrimonyPage() {
  const snapshots = { ...senatorPatrimonyFirst16, ...senatorPatrimonySecond16 };
  const rows = senators
    .map((senator) => ({ senator, snapshot: snapshots[senator.id] }))
    .sort((a, b) => {
      const aValue = a.snapshot?.reportedNetWorth ?? a.snapshot?.reportedAssets ?? -1;
      const bValue = b.snapshot?.reportedNetWorth ?? b.snapshot?.reportedAssets ?? -1;
      return bValue - aValue;
    });

  const directPdfCount = rows.filter((item) => item.snapshot?.declarationLinkType === "direct_pdf").length;
  const withNetWorth = rows.filter((item) => item.snapshot?.reportedNetWorth != null).length;
  const withPublishedValue = rows.filter(
    (item) => item.snapshot?.reportedNetWorth != null || item.snapshot?.reportedAssets != null,
  ).length;

  return (
    <>
      <section className="hero">
        <div className="shell">
          <p className="eyebrow">Transparencia patrimonial · Senado 2024–2028</p>
          <h1>Patrimonio y declaraciones juradas de los 32 senadores</h1>
          <p className="lede">
            El OED reúne declaración jurada, activos, pasivos y patrimonio neto cuando la fuente permite identificarlos con precisión. Un aumento o disminución patrimonial no constituye por sí mismo evidencia de irregularidad.
          </p>
          <div className="grid">
            <article className="card"><strong className="metric">32</strong><span>senadores incluidos</span></article>
            <article className="card"><strong className="metric">{withPublishedValue}</strong><span>con cifra patrimonial publicada</span></article>
            <article className="card"><strong className="metric">{withNetWorth}</strong><span>con patrimonio neto identificado</span></article>
            <article className="card"><strong className="metric">{directPdfCount}</strong><span>PDF individuales ya resueltos</span></article>
          </div>
          <p className="profile-actions">
            <Link className="button secondary" href="/poder-legislativo">← Poder Legislativo</Link>
          </p>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <p className="eyebrow">Ranking patrimonial documentado</p>
          <h2>Los 32 senadores</h2>
          <p className="lede">
            El orden usa patrimonio neto cuando está disponible; en su defecto usa el total de activos publicado. Por eso cada tarjeta indica exactamente qué magnitud está documentada y evita presentar activos como si fueran patrimonio neto.
          </p>
          <div className="initiative-list">
            {rows.map(({ senator, snapshot }, index) => (
              <article className="card" key={senator.id}>
                <p className="senator-meta">
                  <span className="badge">#{index + 1}</span>
                  <span>{senator.province}</span>
                  {senator.party ? <span>{senator.party}</span> : null}
                </p>
                <h3>{senator.fullName}</h3>
                {snapshot ? (
                  <>
                    <div className="grid attendance-detail">
                      <article className="card"><strong className="metric">{money(snapshot.reportedAssets)}</strong><span>Activos / total publicado</span></article>
                      <article className="card"><strong className="metric">{money(snapshot.reportedLiabilities)}</strong><span>Pasivos identificados</span></article>
                      <article className="card"><strong className="metric">{money(snapshot.reportedNetWorth)}</strong><span>Patrimonio neto</span></article>
                    </div>
                    <p><strong>Declaración:</strong> {snapshot.declarationPeriod}</p>
                    {snapshot.priorDeclarationId ? <p><strong>Declaración anterior identificada:</strong> {snapshot.priorDeclarationId}</p> : null}
                    {snapshot.note ? <p>{snapshot.note}</p> : null}
                    <p className="senator-links">
                      <a className="button" href={snapshot.declarationUrl} target="_blank" rel="noreferrer">
                        {snapshot.declarationLinkType === "direct_pdf" ? "Ver declaración jurada" : "Abrir fuente oficial"}
                      </a>
                      <a href={snapshot.sourceUrl} target="_blank" rel="noreferrer">Fuente de las cifras</a>
                      <Link href={`/poder-legislativo/senadores/${senator.id}`}>Expediente completo</Link>
                    </p>
                  </>
                ) : (
                  <div className="notice">Expediente patrimonial pendiente.</div>
                )}
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section profile-muted-section">
        <div className="shell">
          <p className="eyebrow">Metodología</p>
          <h2>Cómo leer este ranking</h2>
          <div className="grid">
            <article className="card"><h3>Activos ≠ patrimonio neto</h3><p>El patrimonio neto requiere descontar pasivos. Cuando una fuente solo publica un total de activos, el OED lo identifica como tal y deja el neto pendiente.</p></article>
            <article className="card"><h3>Monedas separadas</h3><p>Bienes, deudas o inversiones en dólares no se convierten automáticamente a pesos sin una tasa y fecha explícitas.</p></article>
            <article className="card"><h3>Evolución ≠ irregularidad</h3><p>La variación patrimonial por sí sola no demuestra enriquecimiento ilícito, corrupción ni otra conducta ilegal. El OED muestra documentos y cálculos para análisis público.</p></article>
            <article className="card"><h3>Siguiente capa</h3><p>Para reelectos y exfuncionarios se enlazarán declaraciones anteriores y se calculará la evolución entre fechas comparables, manteniendo activos, pasivos y monedas con la misma metodología.</p></article>
          </div>
        </div>
      </section>
    </>
  );
}
