import type { Metadata } from "next";
import Link from "next/link";

import { senators } from "@/lib/legislators";
import { senatorPatrimonyFirst16 } from "@/lib/senator-patrimony-first16";

export const metadata: Metadata = {
  title: "Patrimonio de senadores",
  description:
    "Declaraciones juradas, activos, pasivos y patrimonio neto documentado de los senadores de la República Dominicana.",
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
  const rows = senators
    .slice(0, 16)
    .map((senator) => ({ senator, snapshot: senatorPatrimonyFirst16[senator.id] }))
    .sort((a, b) => (b.snapshot?.reportedNetWorth ?? -1) - (a.snapshot?.reportedNetWorth ?? -1));

  const directPdfCount = rows.filter((item) => item.snapshot?.declarationLinkType === "direct_pdf").length;
  const withNetWorth = rows.filter((item) => item.snapshot?.reportedNetWorth != null).length;

  return (
    <>
      <section className="hero">
        <div className="shell">
          <p className="eyebrow">Transparencia patrimonial · Senado 2024–2028</p>
          <h1>Patrimonio y declaraciones juradas</h1>
          <p className="lede">
            Primera ola: 16 senadores. El OED reúne la declaración jurada, activos, pasivos y patrimonio neto cuando la fuente permite identificarlos con precisión. Los valores no constituyen una auditoría independiente ni una acusación de irregularidad.
          </p>
          <div className="grid">
            <article className="card"><strong className="metric">16</strong><span>senadores en esta primera ola</span></article>
            <article className="card"><strong className="metric">{directPdfCount}</strong><span>PDF individuales ya resueltos</span></article>
            <article className="card"><strong className="metric">{withNetWorth}</strong><span>con patrimonio neto cuantificado</span></article>
          </div>
          <p className="profile-actions">
            <Link className="button secondary" href="/poder-legislativo">← Poder Legislativo</Link>
          </p>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <p className="eyebrow">Ranking patrimonial documentado</p>
          <h2>Primeros 16 senadores</h2>
          <p className="lede">
            Ordenado por patrimonio neto cuando está disponible. Si una fuente solo publica activos o un total consolidado, el OED lo mantiene separado y no lo presenta como patrimonio neto sin sustento.
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
                      <article className="card"><strong className="metric">{money(snapshot.reportedAssets)}</strong><span>Activos reportados</span></article>
                      <article className="card"><strong className="metric">{money(snapshot.reportedLiabilities)}</strong><span>Pasivos reportados</span></article>
                      <article className="card"><strong className="metric">{money(snapshot.reportedNetWorth)}</strong><span>Patrimonio neto</span></article>
                    </div>
                    <p><strong>Declaración:</strong> {snapshot.declarationPeriod}</p>
                    {snapshot.priorDeclarationId ? <p><strong>Declaración anterior identificada:</strong> {snapshot.priorDeclarationId}</p> : null}
                    {snapshot.note ? <p>{snapshot.note}</p> : null}
                    <p className="senator-links">
                      <a className="button" href={snapshot.declarationUrl} target="_blank" rel="noreferrer">
                        {snapshot.declarationLinkType === "direct_pdf" ? "Ver declaración jurada" : "Abrir portal oficial"}
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
            <article className="card"><h3>Activos ≠ patrimonio neto</h3><p>El patrimonio neto requiere descontar pasivos. El OED evita tratar un total de activos como patrimonio neto cuando la fuente no lo permite.</p></article>
            <article className="card"><h3>Monedas separadas</h3><p>Bienes y cuentas en dólares no se suman automáticamente a pesos dominicanos sin una política explícita de conversión y fecha de tasa.</p></article>
            <article className="card"><h3>Evolución ≠ irregularidad</h3><p>El aumento o disminución patrimonial por sí solo no demuestra enriquecimiento ilícito, corrupción ni otra conducta ilegal. El OED presenta documentos y variaciones para análisis público.</p></article>
          </div>
        </div>
      </section>
    </>
  );
}
