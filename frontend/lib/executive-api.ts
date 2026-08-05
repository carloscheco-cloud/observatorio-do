import type { AuthorityDetail, AuthorityListItem, ChangeItem, ExecutiveSummary, InstitutionDetail, InstitutionListItem, LegalDocument, Page, PersonAuthorityDetail, PublicMediaAsset, PublicMediaCollection, RelationshipItem, TransparencyResponse } from "@/types/executive";

export type ExecutiveApiErrorKind = "not_configured" | "timeout" | "network" | "not_found" | "validation" | "unavailable" | "empty";
export class ExecutiveApiError extends Error { constructor(public kind: ExecutiveApiErrorKind, public status?: number) { super(publicMessage(kind)); this.name = "ExecutiveApiError"; } }
export const publicMessage = (kind: ExecutiveApiErrorKind) => ({not_configured:"La API pública no está configurada.",timeout:"La consulta tardó demasiado. Inténtalo nuevamente.",network:"No fue posible conectar con la API pública.",not_found:"No se localizaron datos públicos para este recurso.",validation:"Los filtros enviados no son válidos.",unavailable:"La API pública no está disponible temporalmente.",empty:"La API devolvió una respuesta vacía."}[kind]);
const configuredBase = () => process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "");
export async function executiveApi<T>(path: string, init: RequestInit = {}): Promise<T> {
  const base = configuredBase();
  if (!base) throw new ExecutiveApiError("not_configured");
  if (!path.startsWith("/")) throw new Error("La ruta debe ser relativa");
  const controller = new AbortController(); const timer = setTimeout(() => controller.abort(), 8000);
  try {
    const response = await fetch(`${base}/api/v1/executive${path}`, {...init, signal: controller.signal, next: {revalidate: 60}});
    if (!response.ok) { if(response.status===404) throw new ExecutiveApiError("not_found",404); if(response.status===422) throw new ExecutiveApiError("validation",422); throw new ExecutiveApiError("unavailable",response.status); }
    const text = await response.text(); if(!text.trim()) throw new ExecutiveApiError("empty");
    return JSON.parse(text) as T;
  } catch(error) { if(error instanceof ExecutiveApiError) throw error; if(error instanceof DOMException && error.name==="AbortError") throw new ExecutiveApiError("timeout"); throw new ExecutiveApiError("network"); }
  finally { clearTimeout(timer); }
}
const query = (params?: URLSearchParams) => params?.size ? `?${params}` : "";
export const executive = {
  summary: () => executiveApi<ExecutiveSummary>("/summary"),
  institutions: (p?: URLSearchParams) => executiveApi<Page<InstitutionListItem>>(`/institutions${query(p)}`),
  institution: (slug:string) => executiveApi<InstitutionDetail>(`/institutions/${encodeURIComponent(slug)}`),
  institutionMedia: (slug:string) => executiveApi<PublicMediaCollection>(`/institutions/${encodeURIComponent(slug)}/media`),
  authority: (slug:string) => executiveApi<AuthorityDetail>(`/institutions/${encodeURIComponent(slug)}/authority`),
  relationships: (slug:string) => executiveApi<RelationshipItem[]>(`/institutions/${encodeURIComponent(slug)}/relationships`),
  legalBasis: (slug:string) => executiveApi<LegalDocument[]>(`/institutions/${encodeURIComponent(slug)}/legal-basis`),
  transparency: (slug:string) => executiveApi<TransparencyResponse>(`/institutions/${encodeURIComponent(slug)}/transparency`),
  authorities: (p?:URLSearchParams) => executiveApi<Page<AuthorityListItem>>(`/authorities${query(p)}`),
  authorityDetail: (id:string) => executiveApi<PersonAuthorityDetail>(`/authorities/${encodeURIComponent(id)}`),
  authorityMedia: (id:string) => executiveApi<PublicMediaCollection>(`/authorities/${encodeURIComponent(id)}/media`),
  mediaAsset: (id:string) => executiveApi<PublicMediaAsset>(`/media/${encodeURIComponent(id)}`),
  changes: (p?:URLSearchParams) => executiveApi<Page<ChangeItem>>(`/changes${query(p)}`),
};
