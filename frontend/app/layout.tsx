import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import "./executive.css";

export const metadata: Metadata = {
  title: { default: "Observatorio del Estado Dominicano", template: "%s | Observatorio" },
  description: "Consulta independiente, trazable y accesible de información pública del Estado dominicano.",
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL!),
  openGraph: { type: "website", locale: "es_DO", title: "Observatorio del Estado Dominicano" },
};

const links = [
  ["/poder-ejecutivo", "Ejecutivo"],
  ["/poder-legislativo", "Legislativo"],
  ["/poder-judicial", "Judicial"],
  ["/presupuesto", "Presupuesto"],
  ["/compras", "Compras"],
  ["/buscar", "Buscar"],
];

export default function RootLayout({ children }: Readonly<{children: React.ReactNode}>) {
  return <html lang="es"><body>
    <a className="skip" href="#contenido">Saltar al contenido</a>
    <header className="top"><div className="shell">
      <Link className="brand" href="/">OBSERVATORIO <small>independiente del Estado dominicano</small></Link>
      <nav className="nav" aria-label="Principal">
        {links.map(([href,label]) => <Link key={href} href={href}>{label}</Link>)}
      </nav>
    </div></header>
    <main id="contenido">{children}</main>
    <footer className="footer"><div className="shell">
      <strong>Observatorio del Estado Dominicano</strong>
      <p>Proyecto independiente. Las señales observables no equivalen a acusaciones.</p>
      <Link href="/metodologia">Metodología</Link> · <Link href="/acerca">Acerca</Link>
    </div></footer>
  </body></html>;
}
