import { senatorInitiatives, type SenatorInitiative } from "@/lib/senate-observation";
import { verifiedSenatorInitiatives } from "@/lib/senator-initiatives-verified";
import { senatorIntegrityPoliticsInitiatives } from "@/lib/senator-integrity-politics-initiative";

export type LegislativeItemType = "bill" | "resolution" | "other";
export type LegislativeRole = "primary" | "cosponsor" | "other";

export type NormalizedSenatorInitiative = SenatorInitiative & {
  type: LegislativeItemType;
  normalizedRole: LegislativeRole;
};

function classifyType(title: string): LegislativeItemType {
  const normalized = title.toLowerCase();
  if (normalized.includes("resolución") || normalized.includes("resolucion")) return "resolution";
  if (normalized.includes("proyecto de ley") || normalized.startsWith("ley ") || normalized.includes(" ley que ")) return "bill";
  return "other";
}

function classifyRole(role?: string): LegislativeRole {
  const normalized = (role ?? "").toLowerCase();
  if (normalized.includes("coproponente") || normalized.includes("acogente")) return "cosponsor";
  if (normalized.includes("proponente") || normalized.includes("autor")) return "primary";
  return "other";
}

function key(item: SenatorInitiative) {
  if (item.number) return `number:${item.number.trim().toLowerCase()}`;
  return `title:${item.title.trim().toLowerCase().replace(/\s+/g, " ")}`;
}

export function getSenatorLegislativeInventory(id: string): NormalizedSenatorInitiative[] {
  const raw = [
    ...(senatorInitiatives[id] ?? []),
    ...(verifiedSenatorInitiatives[id] ?? []),
    ...(senatorIntegrityPoliticsInitiatives[id] ?? []),
  ];

  const deduped = new Map<string, SenatorInitiative>();
  for (const item of raw) {
    const itemKey = key(item);
    const previous = deduped.get(itemKey);
    if (!previous) {
      deduped.set(itemKey, item);
      continue;
    }
    // Prefer the record with the more advanced/explicit state and documentary number.
    const score = (value: SenatorInitiative) =>
      (value.number ? 2 : 0) +
      (value.introducedAt ? 1 : 0) +
      (["promulgated", "approved_congress", "approved_senate", "rejected", "expired", "withdrawn"].includes(value.status) ? 3 : 0);
    if (score(item) > score(previous)) deduped.set(itemKey, item);
  }

  return [...deduped.values()].map((item) => ({
    ...item,
    type: classifyType(item.title),
    normalizedRole: classifyRole(item.role),
  }));
}

export function summarizeSenatorLegislativeInventory(id: string) {
  const items = getSenatorLegislativeInventory(id);
  const count = (predicate: (item: NormalizedSenatorInitiative) => boolean) => items.filter(predicate).length;
  return {
    total: items.length,
    bills: count((item) => item.type === "bill"),
    resolutions: count((item) => item.type === "resolution"),
    primary: count((item) => item.normalizedRole === "primary"),
    cosponsor: count((item) => item.normalizedRole === "cosponsor"),
    introduced: count((item) => item.status === "introduced"),
    committee: count((item) => item.status === "committee"),
    approvedSenate: count((item) => item.status === "approved_senate"),
    approvedCongress: count((item) => item.status === "approved_congress"),
    promulgated: count((item) => item.status === "promulgated"),
    rejected: count((item) => item.status === "rejected"),
    expired: count((item) => item.status === "expired"),
    withdrawn: count((item) => item.status === "withdrawn"),
    unknown: count((item) => item.status === "unknown"),
  };
}
