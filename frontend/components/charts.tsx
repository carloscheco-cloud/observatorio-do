export interface Point { label: string; value: number | null }
function AccessibleChart({ title, data, kind }: { title: string; data: Point[]; kind: string }) {
  const max = Math.max(...data.map(d => d.value ?? 0), 1);
  return <figure className="chart"><figcaption><strong>{title}</strong> · {kind}</figcaption><div className="bars" aria-hidden="true">{data.map(d => <span key={d.label} style={{ height: `${((d.value ?? 0) / max) * 100}%` }} />)}</div><table><caption className="sr-only">Datos alternativos de {title}</caption><tbody>{data.map(d => <tr key={d.label}><th scope="row">{d.label}</th><td>{d.value ?? "No disponible"}</td></tr>)}</tbody></table></figure>;
}
export const TimeSeriesChart = (p: { title: string; data: Point[] }) => <AccessibleChart {...p} kind="serie temporal" />;
export const ComparisonChart = (p: { title: string; data: Point[] }) => <AccessibleChart {...p} kind="comparación" />;
export const DistributionChart = (p: { title: string; data: Point[] }) => <AccessibleChart {...p} kind="distribución" />;
