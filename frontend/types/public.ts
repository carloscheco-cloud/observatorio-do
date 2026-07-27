export type Coverage = "complete" | "partial" | "not_available" | "stale" | "under_review";
export interface Pagination { page: number; page_size: number; total_items: number; total_pages: number; has_next: boolean; has_previous: boolean }
export interface Collection<T> { data: T[]; pagination: Pagination; filters_applied: Record<string, unknown>; sort: string; generated_at: string; source_freshness: string; warnings: string[] }
export interface Institution { id: string; name: string; kind: string; territory_id: string; status: string }
export interface PublicItem<T> { data: T; generated_at: string; source_freshness: string; warnings: string[] }
export interface InstitutionProfile extends Institution {
  legal_basis: { title: string; reference: string; official_url: string | null } | null;
  metrics: Record<string, number>;
  coverage: Record<string, Coverage>;
  data_quality: string;
  last_updated: string | null;
}
export interface SearchResult { id: string; entity_type: string; title: string; subtitle?: string; url: string; score: number }
export interface Summary { data: Record<string, unknown>; availability: string; generated_at: string; warnings: string[] }
