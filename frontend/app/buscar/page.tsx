import Link from "next/link";
import { SearchBar } from "@/components/SearchBar";
import { EmptyState } from "@/components/ui";
import { optional, searchPublic } from "@/lib/api";

export default async function Search({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q = "" } = await searchParams;
  const result = q.length >= 2 ? await optional(searchPublic(q)) : null;
  return (
    <div className="shell section">
      <h1>Buscar</h1>
      <SearchBar initial={q} />
      {result?.data.length ? (
        <ul>
          {result.data.map((item) => (
            <li key={`${item.entity_type}-${item.id}`}>
              <Link href={item.url}>
                <strong>{item.title}</strong>
              </Link>
              {item.subtitle && <span> · {item.subtitle}</span>}
            </li>
          ))}
        </ul>
      ) : (
        <EmptyState title={q ? `Sin resultados públicos para “${q}”` : "Escribe al menos dos caracteres"}>
          Prueba otro nombre, código o tipo de entidad.
        </EmptyState>
      )}
    </div>
  );
}
