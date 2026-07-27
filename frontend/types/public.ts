export type Coverage = "complete" | "partial" | "not_available" | "stale" | "under_review";
export interface Pagination { page: number; page_size: number; total_items: number; total_pages: number; has_next: boolean; has_previous: boolean }
export interface Collection<T> { data: T[]; pagination: Pagination; filters_applied: Record<string, unknown>; sort: string; generated_at: string; source_freshness: string; warnings: string[] }
export interface Institution { id: string; name: string; kind: string; territory_id: string; status: string }
