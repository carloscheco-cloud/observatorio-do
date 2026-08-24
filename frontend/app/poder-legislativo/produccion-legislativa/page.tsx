import type { Metadata } from "next";
import Link from "next/link";

import { senators } from "@/lib/legislators";
import {
  getSenatorLegislativeInventory,
  summarizeSenatorLegislativeInventory,
} from "@/lib/senator-legislative-inventory";

export const metadata: Metadata = {
  title: "Producción legislativa del Senado",
  description: "Inventario documentado de iniciativas, proyectos de ley y resoluciones de los 32 senadores.",
  alternates: { canonical: "/poder-legislativo/produccion-legislativa" },
};

const statusLabel: Record<string, string> = {
  introduced: "Depositada",
  committee: "En comisión",
  approved_senate: "Aprobada por Senado",
  approved_congress: "Aprobada por Congreso",
  promulgated: "Promulgada / ley",
  rejected: "Rechazada",
  expired: "Perimida",
  withdrawn: "Retirada",
  unknown: "Estado por verificar",
};

function typeLabel(type: string) {
  if (type === "bill") return "Proyecto de ley";
  if (type === "resolution") return "Resolución";
  return "Otra iniciativa";
}

export default function SenateLegislativeProductionPage() {
  const rows = senators.map((senator) => ({
    senator,
    summary: summarizeSenatorLegislativeInventory(senator.id),
    items: getSenatorLegislativeInventory(senator.id),
  }));

  const totals = rows.reduce(
    (acc, row) => {
      acc.items += row.summary.total;
      acc.bills += row.summary.bills;
      acc.resolutions += row.summary.resolutions;
      acc.approvedSenate += row.summary.approvedSenate;
      acc.promulgated += row.summary.promulgated;
      acc.rejected += row.summary.rejected;
      acc.expired += row.summary.expired;
      return acc;
    },
    { items: 0, bills: 0, resolutions: 0, approvedSenate: 0, promulgated: 0, rejected: 0, expired: 0 },
  );

  return (
    <>
      <section className="hero">
        <div className="shell">
          <p className="eyebrow">Senado 2024–2028 · Nivel 1</p>
          <h1>Producción legislativa e iniciativas</h1>
          <p className="lede">
            Inventario documental de lo que ha propuesto cada senador y del estado conocido de cada iniciativa. El OED separa autoría principal, copatrocinio, proyectos de ley y resoluciones para evitar inflar la producción individual.
          </p>
          <p>
            Esta primera versión agrega únicamente expedientes ya verificados. El universo seguirá creciendo con la extracción sistemática del SIL, iniciativas aprobadas, perimidas, órdenes del día y actas.
          </p>
          <div className="grid">
            <article className="card"><strong className="metric">32/32</strong><span>senadores con expediente iniciado</span></article>
            <article className="card"><strong className="metric">{totals.items}</strong><span>relaciones senador–iniciativa verificadas</span></article>
            <article className="card"><strong className="metric">{totals.bills}</strong><span>proyectos de ley clasificados</span></article>
            <article className="card"><strong className="metric">{totals.resolutions}</strong><span>resoluciones clasificadas</span></article>
            <article className="card"><strong className="metric">{totals.approvedSenate}</strong><span>relaciones con aprobación del Senado</span></article>
            <article className="card"><strong className="metric">{totals.promulgated}</strong><span>relaciones con ley promulgada</span></article>
          </div>
          <p className="profile-actions"><Link className="button secondary" href="/poder-legislativo">← Poder Legislativo</Link></p>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <p className="eyebrow">Embudo por senador</p>
          <h2>Qué ha propuesto y qué ocurrió</h2>
          <div className="initiative-list">
            {rows.map(({ senator, summary, items }) => (
              <article className="card" key={senator.id}>
                <p className="senator-meta"><span className="badge">{senator.province}</span>{senator.party ? <span>{senator.party}</span> : null}</p>
                <h3><Link href={`/poder-legislativo/senadores/${senator.id}`}>{senator.fullName}</Link></h3>
                <div className="grid attendance-detail">
                  <article className="card"><strong className="metric">{summary.total}</strong><span>iniciativas localizadas</span></article>
                  <article className="card"><strong className="metric">{summary.bills}</strong><span>proyectos de ley</span></article>
                  <article className="card"><strong className="metric">{summary.resolutions}</strong><span>resoluciones</span></article>
                  <article className="card"><strong className="metric">{summary.primary}</strong><span>autor/proponente</span></article>
                  <article className="card"><strong className="metric">{summary.cosponsor}</strong><span>coproponente/acogente</span></article>
                  <article className="card"><strong className="metric">{summary.approvedSenate}</strong><span>aprobadas Senado</span></article>
                  <article className="card"><strong className="metric">{summary.promulgated}</strong><span>promulgadas</span></article>
                  <article className="card"><strong className="metric">{summary.expired}</strong><span>perimidas</span></article>
                  <article className="card"><strong className="metric">{summary.rejected}</strong><span>rechazadas</span></article>
                </div>

                <details>
                  <summary>Ver iniciativas documentadas ({items.length})</summary>
                  <div className="initiative-list" style={{ marginTop: "1rem" }}>
                    {items.map((item, index) => (
                      <article className="card" key={`${senator.id}-${item.number ?? index}`}>
                        <p className="senator-meta">
                          <span className="badge">{typeLabel(item.type)}</span>
                          <span>{statusLabel[item.status] ?? item.status}</span>
                          {item.normalizedRole === "primary" ? <span>Autor/proponente</span> : item.normalizedRole === "cosponsor" ? <span>Coproponente/acogente</span> : null}
                        </p>
                        <h3>{item.title}</h3>
                        {item.number ? <p><strong>Expediente:</strong> {item.number}</p> : null}
                        {item.introducedAt ? <p><strong>Fecha:</strong> {item.introducedAt}</p> : null}
                        {item.role ? <p><strong>Participación:</strong> {item.role}</p> : null}
                        <a href={item.sourceUrl} target="_blank" rel="noreferrer">Ver fuente documental</a>
                      </article>
                    ))}
                  </div>
                </details>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="section profile-muted-section">
        <div className="shell">
          <p className="eyebrow">Reglas OED</p>
          <h2>Cómo se contará la producción</h2>
          <div className="grid">
            <article className="card"><h3>Autoría ≠ firma</h3><p>Un senador que acoge o copatrocina una pieza no se presenta como autor principal. La misma iniciativa puede estar vinculada a varios senadores sin convertirse en varias leyes.</p></article>
            <article className="card"><h3>Ley ≠ resolución</h3><p>Los proyectos de ley se contabilizan aparte de resoluciones, reconocimientos y exhortaciones.</p></article>
            <article className="card"><h3>Estado verificable</h3><p>Aprobada por el Senado no significa promulgada. Congreso, Poder Ejecutivo, perención, rechazo o retiro se registran como etapas diferentes.</p></article>
            <article className="card"><h3>Reintroducciones</h3><p>Cuando una misma propuesta perime y se reintroduce, el siguiente nivel enlazará las versiones dentro de una sola trayectoria legislativa.</p></article>
          </div>
        </div>
      </section>
    </>
  );
}
