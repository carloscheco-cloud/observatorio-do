import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_SITE_URL!;
  const paths = [
    "",
    "instituciones",
    "poder-ejecutivo",
    "poder-ejecutivo/documentacion",
    "poder-ejecutivo/autoridades",
    "poder-ejecutivo/cambios",
    "poder-legislativo",
    "poder-judicial",
    "personas",
    "territorios",
    "nomina",
    "presupuesto",
    "compras",
    "contratos",
    "proveedores",
    "deuda",
    "patrimonio",
    "alertas",
    "buscar",
    "comparar",
    "fuentes",
    "metodologia",
    "acerca",
  ];
  return paths.map((path) => ({ url: `${base}/${path}`, changeFrequency: "weekly" }));
}
