import { SearchBar } from "@/components/SearchBar";
import { EmptyState } from "@/components/ui";
export default async function Search({searchParams}:{searchParams:Promise<{q?:string}>}) { const {q=""}=await searchParams; return <div className="shell section"><h1>Buscar</h1><SearchBar initial={q}/><EmptyState title={q ? `Sin resultados públicos para “${q}”` : "Escribe al menos dos caracteres"}>Prueba otro nombre, código o tipo de entidad.</EmptyState></div> }
