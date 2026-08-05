"use client";
export default function ErrorPage({reset}:{reset:()=>void}){return <div className="shell section empty" role="alert"><h1>No pudimos cargar el Poder Ejecutivo</h1><p>La API pública no está disponible temporalmente.</p><button className="button" onClick={reset}>Reintentar</button></div>}
