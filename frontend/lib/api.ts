import type { Collection, Institution, InstitutionProfile, PublicItem, SearchResult, Summary } from "@/types/public";

const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1/public";

export class PublicApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  if (!path.startsWith("/")) throw new Error("La ruta debe ser relativa");
  const response = await fetch(`${base}${path}`, { ...options, next: { revalidate: 60 } });
  if (!response.ok) throw new PublicApiError(response.status, "No fue posible consultar los datos públicos.");
  return response.json() as Promise<T>;
}

export const getInstitutions = (query = "") =>
  api<Collection<Institution>>(`/institutions${query ? `?q=${encodeURIComponent(query)}` : ""}`);
export const getInstitutionProfile = (id: string) =>
  api<PublicItem<InstitutionProfile>>(`/institutions/${encodeURIComponent(id)}/profile`);
export const getInstitutionSection = (id: string, section: string) =>
  api<Collection<Record<string, unknown>>>(`/institutions/${encodeURIComponent(id)}/${section}`);
export const searchPublic = (query: string) =>
  api<Collection<SearchResult>>(`/search?q=${encodeURIComponent(query)}`);
export const getSummary = (path: string) => api<Summary>(path);
export async function optional<T>(request: Promise<T>): Promise<T | null> {
  try { return await request; } catch { return null; }
}
