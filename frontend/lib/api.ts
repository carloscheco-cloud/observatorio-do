import type { Collection, Institution } from "@/types/public";

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
