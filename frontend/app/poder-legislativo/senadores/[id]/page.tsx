import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { senators } from "@/lib/legislators";
import { senatorCompletion } from "@/lib/senator-completion";
import { verifiedSenatorAssetDeclarations } from "@/lib/senator-asset-declarations-verified";
import { verifiedSenatorAttendance } from "@/lib/senator-attendance-verified";
import { senatorPatrimonyFirst16 } from "@/lib/senator-patrimony-first16";
import { senatorPatrimonySecond16 } from "@/lib/senator-patrimony-second16";
import { senatorPatrimonyHistory } from "@/lib/senator-patrimony-history";
import { provinceLocatorMapUrl, provinceMapAttributionUrl } from "@/lib/province-locator-map";
import {
  senateBenefitResearchNotes,
  senateCompensation,
  senateObservationSources,
  senatorAssetDeclarations,
  senatorInitiatives,
} from "@/lib/senate-observation";

type PageProps = { params: Promise<{ id: string }> };

function getSenator(id: string) {
  const base = senators.find((item) => item.id === id);
  if (!base) return null;
  return { ...base, ...senatorCompletion[id], photoUrl: base.photoUrl ?? `/api/senator-photo/${base.id}` };
}

function money(value?: number) {
  if (value == null) return null;
  return new Intl.NumberFormat("es-DO", {
    style: "currency",
    currency: "DOP",
    maximumFractionDigits: 0,
  }).format(value);
}

function percentage(value: number) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(1)}%`;
}

function benefitValue(item: (typeof senateCompensation)[number]) {
  if (item.amount != null) return money(item.amount);
  if (item.unit === "per_two_years") return "1 vehículo / 2 años";
  if (item.unit === "entitlement") return "Derecho institucional";
  return "Monto individual variable";
}

function benefitUnit(item: (typeof senateCompensation)[number]) {
  if (item.unit === "monthly") return "mensual";
  if (item.unit === "per_session") return "por sesión";
  if (item.unit === "per_two_years") return "beneficio tributario";
  if (item.unit === "entitlement") return "soporte/derecho";
  return "verificar por senador";
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

function declarationTypeLabel(type: "inicio" | "actualizacion" | "cese") {
  if (type === "inicio") return "Inicio en el cargo";
  if (type === "actualizacion") return "Actualización";
  return "Cese en el cargo";
}

export function generateStaticParams() {
  return senators.map((senator) => ({ id: senator.id }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params;
  const senator = getSenator(id);
  if (!senator) return { title: "Senador no encontrado" };
  return {
    title: `${senator.fullName} · Senado`,
    description: `Expediente público de ${senator.fullName}: formación, patrimonio, remuneración, asistencia e iniciativas legislativas documentadas por el OED.`,
    alternates: { canonical: `/poder-legislativo/senadores/${senator.id}` },
  };
}

export default async function SenatorProfilePage({ params }: PageProps) {
  const { id } = await params;
  const senator = getSenator(id);
  if (!senator) notFound();

  const attendance = verifiedSenatorAttendance[senator.id] ?? [];
  const latestAttendance = attendance[attendance.length - 1];
  const initiatives = senatorInitiatives[senator.id] ?? [];
  const declarations = [
    ...(senatorAssetDeclarations[senator.id] ?? []),
    ...(verifiedSenatorAssetDeclarations[senator.id] ?? []),
  ].sort((a, b) => a.date.localeCompare(b.date));

  const snapshot = senatorPatrimonyFirst16[senator.id] ?? senatorPatrimonySecond16[senator.id];
  const history = senatorPatrimonyHistory[senator.id] ?? [];
  const latestDeclaration = declarations[declarations.length - 1];
  const currentNetWorth = snapshot?.reportedNetWorth;
  const comparableHistoricalPoint = [...history]
    .reverse()
    .find((point) => point.comparability === "comparable" && point.reportedNetWorth != null);
  const historicalNetWorth = comparableHistoricalPoint?.reportedNetWorth;
  const patrimonyChange =
    currentNetWorth != null && historicalNetWorth != null ? currentNetWorth - historicalNetWorth : null;
  const patrimonyChangeRate =
    patrimonyChange != null && historicalNetWorth ? (patrimonyChange / historicalNetWorth) * 100 : null;
  const declarationCount = declarations.length + history.filter((point) => point.sourceUrl).length;
  const declarationUrl = snapshot?.declarationUrl ?? latestDeclaration?.sourceUrl ?? senateObservationSources.declarations;
  const declarationIsDirect = snapshot?.declarationLinkType === "direct_pdf" || Boolean(latestDeclaration);

  const provinceMap = provinceLocatorMapUrl(senator.province);

  return (
    <>
      <section className="hero senator-profile-hero">
        <div className="shell">
          <p className="eyebrow">Expediente legislativo · Senado 2024–2028</p>
          <div className="senator-profile-head">
            <div className="senator-profile-photo">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={senator.photoUrl} alt={senator.fullName} />
            </div>
            <div>
              <p className="senator-meta">
                <span className="badge">{senator.province}</span>
                {senator.party ? <span>{senator.party}</span> : null}
              </p>
              <h1>{senator.fullName}</h1>
              <p className="lede">
                Senador/a de la República por {senator.province}. El OED separa datos verificados,
                parciales y pendientes para que cada cifra pueda ser auditada.
              </p>
              <p>
                <Link className="button secondary" href="/poder-legislativo#senadores">
                  ← Volver al Senado
                </Link>
              </p>
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
              {provinceMap ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  className="province-map-image"
                  src={provinceMap}
                  alt={`Mapa de República Dominicana con ${senator.province} resaltada`}
                  loading="lazy"
                />
              ) : (
                <div className="province-map-fallback">Mapa territorial en preparación</div>
              )}
              <div className="province-map-caption">
                <strong>{senator.province}</strong>
                <span>1 senador representa esta provincia en el Senado.</span>
                <a href={provinceMapAttributionUrl} target="_blank" rel="noreferrer">
                  Mapa: Wikimedia Commons · CC BY-SA
                </a>
              </div>
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
              <div className="notice">
                {senator.educationNote ?? "No se ha localizado formación académica verificable."}
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="section patrimony-section">
        <div className="shell">
          <p className="eyebrow">Transparencia patrimonial</p>
          <h2>Patrimonio y declaraciones juradas</h2>
          <p className="lede">
            El expediente combina la declaración vigente con todas las referencias históricas localizadas. Una variación patrimonial no implica por sí sola irregularidad.
          </p>

          <div className="grid">
            <article className="card">
              <span className="source-status source-verified">Ley 311-14</span>
              <h3>Declaraciones y referencias localizadas</h3>
              <strong className="metric">{declarationCount || (snapshot ? 1 : 0)}</strong>
              <p><strong>Último corte:</strong> {snapshot?.declarationPeriod ?? latestDeclaration?.date ?? "Pendiente"}</p>
              <p className="profile-actions">
                <a className="button" href={declarationUrl} target="_blank" rel="noreferrer">
                  {declarationIsDirect ? "Ver declaración jurada" : "Abrir fuente oficial"}
                </a>
              </p>
            </article>

            <article className="card">
              <h3>Patrimonio neto declarado</h3>
              <strong className="metric">{currentNetWorth != null ? money(currentNetWorth) : "No calculado"}</strong>
              {snapshot?.reportedAssets != null ? <p><strong>Activos:</strong> {money(snapshot.reportedAssets)}</p> : null}
              {snapshot?.reportedLiabilities != null ? <p><strong>Pasivos:</strong> {money(snapshot.reportedLiabilities)}</p> : null}
              {currentNetWorth == null && snapshot?.reportedAssets != null ? (
                <p>La fuente publica activos/total, pero todavía no existe un pasivo comparable para calcular patrimonio neto.</p>
              ) : null}
            </article>

            <article className="card">
              <h3>Evolución patrimonial</h3>
              <strong className="metric">{patrimonyChange != null ? money(patrimonyChange) : history.length ? "Historia disponible" : "Sin serie previa"}</strong>
              {patrimonyChangeRate != null ? <p><strong>Variación comparable:</strong> {percentage(patrimonyChangeRate)}</p> : null}
              {comparableHistoricalPoint ? (
                <p>{comparableHistoricalPoint.date} → {snapshot?.declarationPeriod ?? "última disponible"}</p>
              ) : history.length ? (
                <p>Hay referencias históricas, pero no todas usan la misma metodología para calcular un porcentaje.</p>
              ) : (
                <p>No se ha localizado todavía una declaración patrimonial anterior comparable.</p>
              )}
            </article>
          </div>

          {history.length || snapshot ? (
            <>
              <h3 className="research-heading">Evolución e historia patrimonial</h3>
              <div className="declaration-timeline">
                {history.map((point, index) => (
                  <article className="card" key={`${senator.id}-history-${point.date}-${index}`}>
                    <p className="senator-meta">
                      <span className="badge">{point.date}</span>
                      <span>{point.comparability === "comparable" ? "Comparable" : point.comparability === "partial" ? "Referencia parcial" : "Referencia documental"}</span>
                    </p>
                    {point.office ? <h3>{point.office}</h3> : null}
                    {point.reportedAssets != null ? <p><strong>Activos:</strong> {money(point.reportedAssets)}</p> : null}
                    {point.reportedLiabilities != null ? <p><strong>Pasivos:</strong> {money(point.reportedLiabilities)}</p> : null}
                    {point.reportedNetWorth != null ? <p><strong>Patrimonio neto:</strong> {money(point.reportedNetWorth)}</p> : null}
                    {point.reportedAmount != null ? <p><strong>{point.reportedAmountLabel ?? "Monto publicado"}:</strong> {money(point.reportedAmount)}</p> : null}
                    {point.note ? <p>{point.note}</p> : null}
                    <a href={point.sourceUrl} target="_blank" rel="noreferrer">Ver fuente histórica</a>
                  </article>
                ))}

                {snapshot ? (
                  <article className="card">
                    <p className="senator-meta"><span className="badge">{snapshot.declarationPeriod}</span><span>Última disponible</span></p>
                    <h3>Declaración patrimonial actual</h3>
                    {snapshot.reportedAssets != null ? <p><strong>Activos:</strong> {money(snapshot.reportedAssets)}</p> : null}
                    {snapshot.reportedLiabilities != null ? <p><strong>Pasivos:</strong> {money(snapshot.reportedLiabilities)}</p> : null}
                    {snapshot.reportedNetWorth != null ? <p><strong>Patrimonio neto:</strong> {money(snapshot.reportedNetWorth)}</p> : null}
                    {snapshot.priorDeclarationId ? <p><strong>Declaración anterior identificada:</strong> {snapshot.priorDeclarationId}</p> : null}
                    {snapshot.note ? <p>{snapshot.note}</p> : null}
                    <a href={snapshot.sourceUrl} target="_blank" rel="noreferrer">Ver fuente actual</a>
                  </article>
                ) : null}
              </div>
            </>
          ) : (
            <div className="notice">Todavía no se ha localizado una serie patrimonial verificable para este senador.</div>
          )}

          {declarations.length ? (
            <>
              <h3 className="research-heading">Documentos oficiales enlazados</h3>
              <div className="declaration-timeline">
                {declarations.map((declaration) => (
                  <article className="card" key={`${senator.id}-${declaration.date}-${declaration.type}-${declaration.sourceUrl}`}>
                    <span className="badge">{declarationTypeLabel(declaration.type)}</span>
                    <h3>{declaration.date}</h3>
                    {declaration.assets != null ? <p><strong>Activos:</strong> {money(declaration.assets)}</p> : null}
                    {declaration.liabilities != null ? <p><strong>Pasivos:</strong> {money(declaration.liabilities)}</p> : null}
                    {declaration.netWorth != null ? <p><strong>Patrimonio neto:</strong> {money(declaration.netWorth)}</p> : null}
                    {declaration.note ? <p>{declaration.note}</p> : null}
                    <a href={declaration.sourceUrl} target="_blank" rel="noreferrer">Abrir PDF oficial</a>
                  </article>
                ))}
              </div>
            </>
          ) : null}

          <p className="profile-actions">
            <Link className="button secondary" href="/poder-legislativo/patrimonio/evolucion">Comparar evolución de los 32 senadores</Link>
            <a href={senateObservationSources.declarationLaw} target="_blank" rel="noreferrer">Ver Ley 311-14</a>
          </p>
        </div>
      </section>

      <section className="section profile-muted-section">
        <div className="shell">
          <p className="eyebrow">Remuneración, fondos y privilegios documentados</p>
          <h2>¿Qué recibe realmente un senador?</h2>
          <p className="lede">
            El OED separa ingreso personal, apoyo institucional, fondos sociales y beneficios tributarios.
          </p>
          <div className="compensation-grid">
            {senateCompensation.map((item) => (
              <article className={`card compensation-card benefit-${item.kind}`} key={item.label}>
                <span className={`source-status source-${item.status}`}>
                  {item.status === "verified" ? "Documentado" : item.status === "reported" ? "Reportado" : "Requiere actualización"}
                </span>
                <h3>{item.label}</h3>
                <strong className="benefit-value">{benefitValue(item)}</strong>
                <p className="benefit-unit">{benefitUnit(item)}</p>
                <p>{item.description}</p>
                {item.legalBasis ? <p className="legal-basis"><strong>Base legal:</strong> {item.legalBasis}</p> : null}
                <a href={item.sourceUrl} target="_blank" rel="noreferrer">Fuente documental</a>
              </article>
            ))}
          </div>
          <h3 className="research-heading">Beneficios que todavía requieren prueba individual vigente</h3>
          <div className="research-note-grid">
            {senateBenefitResearchNotes.map((item) => (
              <article className="card" key={item.claim}><strong>{item.claim}</strong><p>{item.note}</p></article>
            ))}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="shell">
          <p className="eyebrow">Actividad parlamentaria</p>
          <h2>Asistencia a plenarias</h2>
          {latestAttendance ? (
            <>
              <p className="senator-note">Período medido: {latestAttendance.period}</p>
              <div className="attendance-score">
                <div><span className="attendance-number">{latestAttendance.presenceRate}%</span><strong>Presencia</strong></div>
                <div><span className="absence-number">{latestAttendance.absenceRate}%</span><strong>Ausencia sin excusa</strong></div>
              </div>
              <div className="attendance-bar" aria-label={`${latestAttendance.presenceRate}% presencia, ${latestAttendance.excusedRate}% excusa y ${latestAttendance.absenceRate}% ausencia sin excusa`}>
                <span className="attendance-bar-present" style={{ width: `${latestAttendance.presenceRate}%` }} />
                <span className="attendance-bar-excused" style={{ width: `${latestAttendance.excusedRate}%` }} />
                <span className="attendance-bar-absent" style={{ width: `${latestAttendance.absenceRate}%` }} />
              </div>
              <div className="grid attendance-detail">
                <article className="card"><strong className="metric">{latestAttendance.presenceRate}%</strong><span>Presencia</span></article>
                <article className="card"><strong className="metric">{latestAttendance.excusedRate}%</strong><span>Excusas</span></article>
                <article className="card"><strong className="metric">{latestAttendance.absenceRate}%</strong><span>Ausencias sin excusa</span></article>
                <article className="card"><strong className="metric">{latestAttendance.plenarySessions ?? "—"}</strong><span>Sesiones con conteo publicado</span></article>
              </div>
              {latestAttendance.plenarySessions != null ? (
                <p>
                  <strong>Detalle:</strong> {latestAttendance.attended ?? 0} presencias, {latestAttendance.excused ?? 0} excusas y {latestAttendance.unjustifiedAbsences ?? 0} ausencias sin excusa de {latestAttendance.plenarySessions} sesiones.
                </p>
              ) : (
                <p>La fuente oficial publica los porcentajes, pero no un conteo consolidado de sesiones en la sección utilizada por el OED.</p>
              )}
              <p><a className="button" href={latestAttendance.sourceUrl} target="_blank" rel="noreferrer">Ver fuente de asistencia</a></p>
            </>
          ) : (
            <div className="attendance-pending">
              <strong>Porcentaje pendiente de cálculo documental</strong>
              <span>El OED todavía no ha consolidado un informe identificable de asistencia para este senador.</span>
            </div>
          )}
        </div>
      </section>

      <section className="section profile-muted-section">
        <div className="shell">
          <p className="eyebrow">Producción legislativa</p>
          <h2>Proyectos e iniciativas impulsadas</h2>
          <p className="lede">Autoría, fecha, número, estado legislativo, resultado y documento original cuando esté disponible.</p>
          {initiatives.length ? (
            <div className="initiative-list">
              {initiatives.map((initiative, index) => (
                <article className="card" key={`${senator.id}-initiative-${index}`}>
                  <p className="senator-meta">
                    {initiative.number ? <span className="badge">{initiative.number}</span> : null}
                    <span>{statusLabel(initiative.status)}</span>
                  </p>
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
            <div className="notice">Expediente individual de iniciativas pendiente de importación. Esto no significa cero proyectos.</div>
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
            <article className="card"><h3>Perfil oficial</h3><a href={senator.officialProfileUrl} target="_blank" rel="noreferrer">Abrir fuente</a></article>
            <article className="card"><h3>Asistencia</h3><a href={senateObservationSources.attendance} target="_blank" rel="noreferrer">Abrir fuente</a></article>
            <article className="card"><h3>Iniciativas</h3><a href={senateObservationSources.initiatives} target="_blank" rel="noreferrer">Abrir fuente</a></article>
            <article className="card"><h3>Datos abiertos</h3><a href={senateObservationSources.openData} target="_blank" rel="noreferrer">Abrir fuente</a></article>
          </div>
        </div>
      </section>
    </>
  );
}
