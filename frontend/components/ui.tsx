import Link from "next/link";
import type { ReactNode } from "react";

export function MetricCard({ label, value, note }: { label: string; value: ReactNode; note?: string }) {
  return <article className="card"><p className="eyebrow">{label}</p><strong className="metric">{value}</strong>{note && <small>{note}</small>}</article>;
}
export function StatusBadge({ children }: { children: ReactNode }) { return <span className="badge">{children}</span>; }
export const SeverityBadge = StatusBadge;
export function FreshnessIndicator({ value = "Sin fecha pública" }: { value?: string }) { return <span aria-label={`Frescura: ${value}`}>Actualización: {value}</span>; }
export function EmptyState({ title = "No hay datos disponibles", children }: { title?: string; children?: ReactNode }) { return <section className="empty"><h2>{title}</h2><p>{children ?? "La ausencia de información no representa un valor de cero."}</p></section>; }
export function ErrorState() { return <section role="alert" className="empty"><h2>No pudimos cargar esta información</h2><p>Inténtalo de nuevo más tarde.</p></section>; }
export function LoadingSkeleton() { return <div className="skeleton" role="status"><span className="sr-only">Cargando</span></div>; }
export function MethodologyNotice() { return <aside className="notice"><strong>Cómo leer estos datos.</strong> Las señales son hechos observables para revisión; no equivalen a acusaciones.</aside>; }
export function Breadcrumbs({ items }: { items: { href: string; label: string }[] }) { return <nav aria-label="Migas de pan"><ol className="crumbs">{items.map(item => <li key={item.href}><Link href={item.href}>{item.label}</Link></li>)}</ol></nav>; }
export function Pagination({ page, total }: { page: number; total: number }) { return <nav aria-label="Paginación"><span>Página {page} de {Math.max(total, 1)}</span></nav>; }
export function ExportButton({ resource }: { resource: string }) {
  const base = process.env.NEXT_PUBLIC_API_URL;
  if (!base) throw new Error("NEXT_PUBLIC_API_URL is required");
  return <a className="button secondary" href={`${base.replace(/\/$/, "")}/export?resource=${encodeURIComponent(resource)}&format=csv`}>Exportar CSV</a>;
}
export function DataTable({ headers, rows }: { headers: string[]; rows: ReactNode[][] }) { return <div className="table-wrap"><table><thead><tr>{headers.map(h => <th scope="col" key={h}>{h}</th>)}</tr></thead><tbody>{rows.map((row, i) => <tr key={i}>{row.map((cell, j) => <td key={j}>{cell}</td>)}</tr>)}</tbody></table></div>; }
export function SourceList() { return <EmptyState title="Fuentes por documentar" />; }
export function EvidenceSummary() { return <p>La evidencia pública enlazada aparecerá aquí cuando esté disponible.</p>; }
