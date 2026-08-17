import type { Metadata } from "next";
import Link from "next/link";

import { ApiState, date, display, ExecutiveNav } from "@/components/executive";
import { MetricCard, StatusBadge } from "@/components/ui";
import { executive, ExecutiveApiError } from "@/lib/executive-api";

export const metadata: Metadata = {
  title: "Documentación ampliada del Poder Ejecutivo",
  description: "Instituciones del Poder Ejecutivo con autoridad, evaluación documental y ficha ampliada disponible.",
  alternates: { canonical: "/poder-ejecutivo/documentacion" },
};

type SP = Record<string, string | string[] | undefined>;
const one = (value: string | string[] | undefined) => Array.isArray(value) ? value[0] : value;

export default async function ExecutiveDocumentationPage({
  searchParams,
}: {
  searchParams: Promise<SP>;
}) {
  const sp = await searchParams;
  const params = new URLSearchParams();
  for (const key of [
    "search",
    "institution_type",
    "has_current_authority",
    "has_transparency_assessment",
    "maturity_status",
    "sort_by",
    "sort_order",
    "page",
  ]) {
    const value = one(sp[key]);
    if (value) params.set(key, value);
  }
  params.set("page_size", "10");

  try {
    const [summary, list] = await Promise.all([
      executive.summary(),
      executive.institutions(params),
    ]);

    return (
      <>
        <section className="hero">
          <div className="shell">
            <p className="eyebrow">Capa documental ampliada</p>
            <h1>Documentación ampliada del Poder Ejecutivo</h1>
            <p className="lede">
              Consulta las instituciones que ya cuentan con mayor profundidad documental dentro del
              OED: autoridad, evaluación, relaciones y otras dimensiones incorporadas por fases.
            </p>
            <ExecutiveNav />
          </div>
        </section>

        <div className="shell section">
          <aside className="notice">
            <strong>Esta no es la cobertura total del Ejecutivo.</strong>
            <p>
              El directorio completo vive en <Link href="/poder-ejecutivo">Poder Ejecutivo</Link>.
              Esta sección conserva la capa más profunda del MVP documental anterior mientras las
              demás instituciones se enriquecen de forma continua.
            </p>
          </aside>

          <p><strong>Alcance documental:</strong> {summary.data_scope}</p>
          <p>Última actualización: {date(summary.latest_data_update)}</p>

          <div className="grid metrics">
            <MetricCard label="Instituciones con ficha ampliada" value={summary.total_institutions} />
            <MetricCard label="Autoridades actuales" value={summary.total_current_authorities} />
            <MetricCard label="Con evaluación" value={summary.institutions_with_transparency_assessment} />
            <MetricCard label="Evaluaciones completas" value={summary.institutions_with_complete_assessment} />
            <MetricCard label="Evaluaciones parciales" value={summary.institutions_with_partial_assessment} />
          </div>

          <form className="filters" role="search">
            <label>
              Buscar institución
              <input name="search" defaultValue={one(sp.search)} />
            </label>
            <label>
              Tipo
              <select name="institution_type" defaultValue={one(sp.institution_type) ?? ""}>
                <option value="">Todos</option>
                <option value="ministry">Ministerio</option>
                <option value="presidency">Presidencia</option>
                <option value="vice_presidency">Vicepresidencia</option>
              </select>
            </label>
            <label>
              Autoridad
              <select name="has_current_authority" defaultValue={one(sp.has_current_authority) ?? ""}>
                <option value="">Todas</option>
                <option value="true">Disponible</option>
                <option value="false">No localizada</option>
              </select>
            </label>
            <label>
              Evaluación
              <select name="has_transparency_assessment" defaultValue={one(sp.has_transparency_assessment) ?? ""}>
                <option value="">Todas</option>
                <option value="true">Evaluada</option>
                <option value="false">Pendiente</option>
              </select>
            </label>
            <button className="button">Aplicar filtros</button>
          </form>

          {list.items.length === 0 ? (
            <p className="empty">No se localizaron instituciones con estos filtros.</p>
          ) : (
            <div className="directory">
              {list.items.map((institution) => (
                <article className="card" key={institution.slug}>
                  <div>
                    <StatusBadge>{institution.status}</StatusBadge>
                    <p className="eyebrow">{institution.institution_type}</p>
                    <h3>{institution.official_name}</h3>
                    <p>{display(institution.short_name)}</p>
                  </div>
                  <dl>
                    <dt>Autoridad actual</dt>
                    <dd>{institution.current_authority_summary?.public_name ?? "No localizada"}</dd>
                    <dt>Puntuación documental</dt>
                    <dd>{institution.latest_transparency_summary?.normalized_score ?? "Pendiente"}</dd>
                    <dt>Cobertura documental</dt>
                    <dd>
                      {institution.latest_transparency_summary
                        ? `${institution.latest_transparency_summary.coverage_percentage}%`
                        : "Pendiente"}
                    </dd>
                    <dt>Verificación</dt>
                    <dd>{date(institution.last_verified_at)}</dd>
                  </dl>
                  <p>
                    <Link className="button" href={`/poder-ejecutivo/instituciones/${institution.slug}`}>
                      Ver ficha ampliada
                    </Link>
                  </p>
                </article>
              ))}
            </div>
          )}

          <nav className="pagination" aria-label="Paginación">
            <span>Página {list.page} de {Math.max(list.pages, 1)}</span>
            {list.page > 1 && <Link href={{ query: { ...sp, page: list.page - 1 } }}>Anterior</Link>}
            {list.page < list.pages && <Link href={{ query: { ...sp, page: list.page + 1 } }}>Siguiente</Link>}
          </nav>
        </div>
      </>
    );
  } catch (error) {
    return (
      <div className="shell section">
        <h1>Documentación ampliada del Poder Ejecutivo</h1>
        <ApiState
          message={
            error instanceof ExecutiveApiError
              ? error.message
              : "No fue posible procesar la respuesta pública."
          }
        />
      </div>
    );
  }
}
