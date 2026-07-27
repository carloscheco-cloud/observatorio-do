import { EmptyState, MethodologyNotice, SeverityBadge } from "@/components/ui";
import { api, optional } from "@/lib/api";
import type { PublicItem } from "@/types/public";

export default async function Finding({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const finding = await optional(api<PublicItem<Record<string, unknown>>>(`/findings/${encodeURIComponent(id)}`));
  if (!finding) return <div className="shell section"><EmptyState title="Alerta pública no disponible" /></div>;
  return <div className="shell section">
    <p className="eyebrow">Alerta pública revisada</p>
    <h1>{String(finding.data.title)}</h1>
    <SeverityBadge>{String(finding.data.severity)}</SeverityBadge>
    <p>{String(finding.data.explanation)}</p>
    <MethodologyNotice />
  </div>;
}
