"use client";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
export function SearchBar({ initial = "" }: { initial?: string }) {
  const [q, setQ] = useState(initial); const router = useRouter();
  function submit(event: FormEvent) { event.preventDefault(); if (q.trim().length >= 2) router.push(`/buscar?q=${encodeURIComponent(q.trim())}`); }
  return <form className="search" role="search" action="/buscar" method="get" onSubmit={submit}><label htmlFor="global-search">Buscar en el Estado</label><div><input id="global-search" name="q" value={q} onChange={e => setQ(e.target.value)} minLength={2} maxLength={120} placeholder="Institución, cargo, contrato o territorio" /><button>Buscar</button></div></form>;
}
