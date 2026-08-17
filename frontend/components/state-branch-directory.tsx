import Link from "next/link";

import { EmptyState, MetricCard } from "@/components/ui";
import { optional } from "@/lib/api";
import {
  coverageLabel,
  getStateCoverage,
  getStateInstitutions,
  institutionTypeLabel,
  type StateBranch,
} from "@/lib/state-api";

type SearchParams = Record<string, string | string[] | undefined>;

const one = (value: string | string[] | undefined) =>
  Array.isArray(value) ? value[0] : value;

export async function StateBranchDirectory({
  branch,
  title,
  description,
  searchParams = {},
  compactHeader = false,
}: {
  branch: StateBranch;
  title: string;
  description: string;
  searchParams?: SearchParams;
  compactHeader?: boolean;
}) {
  const [response, coverage] = await Promise.all([
    optional(getStateInstitutions(branch)),
    optional(getStateCoverage()),
  ]);

  const query = (one(searchParams.search) ?? "").trim().toLocaleLowerCase("es");
  const type = (one(searchParams.institution_type) ?? "").trim();
  const institutions = (response?.data ?? []).filter((institution) => {
    const matchesQuery =
      !query ||
      institution.name.toLocaleLowerCase("es").includes(query) ||
      (institution.acronym ?? "").toLocaleLowerCase("es").includes(query);
    const matchesType = !type || institution.institution_type === type;
    return matchesQuery && matchesType;
  });

  const branchCoverage = coverage?.branches[branch];
  const types = Array.from(
    new Set((response?.data ?? []).map((item) => item.institution_type).filter(Boolean)),
  ).sort() as string[];

  return (
    <div className="shell section">
      {!compactHeader && <p className="eyebrow">Observatorio del Estado Dominicano</p>}
      {compactHeader ? <h2>{title}</h2> : <h1>{title}</h1>}
      <p className="lede">{description}</p>

      <div className="grid metrics">
        <MetricCard
          label="Instituciones documentadas"
          value={response?.pagination.total_items ?? "No disponible"}
        />
        <MetricCard
          label="Con ficha básica o mejor"
          value={branchCoverage?.basic_or_better ?? "No disponible"}
        />
        <MetricCard
          label="Cobertura básica"
          value={
            branchCoverage
              ? `${Math.round(branchCoverage.basic_ratio * 100)}%`
              : "No disponible"
          }
        />
      </div>

      <aside className="notice">
        <strong>Cobertura viva</strong>
        <p>
          Esta superficie lee directamente las instituciones confirmadas del OED. Una ficha básica
          publica identidad institucional y procedencia disponible; la profundidad documental se
          agrega de forma iterativa y no debe interpretarse como una evaluación de desempeño.
        </p>
      </aside>

      <form className="filters" role="search">
        <label>
          Buscar institución
          <input name="search" defaultValue={one(searchParams.search)} />
        </label>
        <label>
          Tipo
          <select name="institution_type" defaultValue={type}>
            <option value="">Todos</option>
            {types.map((item) => (
              <option value={item} key={item}>
                {institutionTypeLabel(item, item)}
              </option>
            ))}
          </select>
        </label>
        <button className="button">Aplicar filtros</button>
      </form>

      <p>
        Mostrando <strong>{institutions.length}</strong> de{" "}
        <strong>{response?.pagination.total_items ?? 0}</strong> instituciones confirmadas.
      </p>

      {institutions.length > 0 ? (
        <div className="directory">
          {institutions.map((institution) => (
            <article className="card" key={institution.id}>
              <div>
                <p className="eyebrow">
                  {institution.acronym ?? institutionTypeLabel(institution.institution_type, institution.kind)}
                </p>
                <h3>{institution.name}</h3>
                <p>{institutionTypeLabel(institution.institution_type, institution.kind)}</p>
                <p>
                  <strong>{coverageLabel(institution.coverage_level)}</strong> · Estado:{" "}
                  {institution.operational_status}
                </p>
              </div>
              <p>
                <Link className="button" href={`/instituciones/${institution.id}`}>
                  Ver ficha pública
                </Link>
              </p>
              {institution.official_website && (
                <p>
                  <a href={institution.official_website} target="_blank" rel="noreferrer">
                    Portal oficial
                  </a>
                </p>
              )}
            </article>
          ))}
        </div>
      ) : (
        <EmptyState title="No hay instituciones que coincidan con estos filtros" />
      )}

      {(response?.warnings ?? []).length > 0 && (
        <section>
          <h2>Notas de cobertura</h2>
          <ul>{response?.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>
        </section>
      )}
    </div>
  );
}
