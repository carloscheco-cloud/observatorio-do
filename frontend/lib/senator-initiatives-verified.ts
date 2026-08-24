import type { SenatorInitiative } from "@/lib/senate-observation";

export const verifiedSenatorInitiatives: Record<string, SenatorInitiative[]> = {
  "moises-ayala-perez": [
    {
      number: "00183-2024-SLO-SE",
      title: "Resolución que solicita al CNSS y a SISALRIL incluir cobertura total para mujeres que padecen gigantomastia",
      role: "Proponente",
      status: "approved_senate",
      introducedAt: "03/11/2024",
      sourceUrl: "https://www.senadord.gob.do/Descargas/1389/iniciativas-aprobadas/50469/diciembre",
    },
    {
      number: "00235-2024-SLO-SE",
      title: "Resolución para promover actividades de promoción, educación y prevención de la salud del hombre",
      role: "Coproponente",
      status: "approved_senate",
      sourceUrl: "https://www.senadord.gob.do/senadores-favorecen-resolucion-promueve-educacion-y-prevencion-de-la-salud-del-hombre-en-el-pais/",
    },
  ],
  "daniel-enrique-rivera-reyes": [
    { number: "00235-2024-SLO-SE", title: "Resolución para promover actividades de promoción, educación y prevención de la salud del hombre", role: "Coproponente", status: "approved_senate", sourceUrl: "https://www.senadord.gob.do/senadores-favorecen-resolucion-promueve-educacion-y-prevencion-de-la-salud-del-hombre-en-el-pais/" },
  ],
  "lia-ynocencia-diaz-santana": [
    { number: "00235-2024-SLO-SE", title: "Resolución para promover actividades de promoción, educación y prevención de la salud del hombre", role: "Coproponente", status: "approved_senate", sourceUrl: "https://www.senadord.gob.do/senadores-favorecen-resolucion-promueve-educacion-y-prevencion-de-la-salud-del-hombre-en-el-pais/" },
  ],
  "dagoberto-rodriguez-adames": [
    { number: "00235-2024-SLO-SE", title: "Resolución para promover actividades de promoción, educación y prevención de la salud del hombre", role: "Coproponente", status: "approved_senate", sourceUrl: "https://www.senadord.gob.do/senadores-favorecen-resolucion-promueve-educacion-y-prevencion-de-la-salud-del-hombre-en-el-pais/" },
  ],
  "jonhson-encarnacion-diaz": [
    { number: "00235-2024-SLO-SE", title: "Resolución para promover actividades de promoción, educación y prevención de la salud del hombre", role: "Coproponente", status: "approved_senate", sourceUrl: "https://www.senadord.gob.do/senadores-favorecen-resolucion-promueve-educacion-y-prevencion-de-la-salud-del-hombre-en-el-pais/" },
  ],
  "odalis-rafael-rodriguez-rodriguez": [
    { number: "00235-2024-SLO-SE", title: "Resolución para promover actividades de promoción, educación y prevención de la salud del hombre", role: "Coproponente", status: "approved_senate", sourceUrl: "https://www.senadord.gob.do/senadores-favorecen-resolucion-promueve-educacion-y-prevencion-de-la-salud-del-hombre-en-el-pais/" },
  ],
};

const electoralReformSponsors = [
  "ramon-rogelio-genao-duran",
  "pedro-manuel-catrain-bonilla",
  "moises-ayala-perez",
  "maria-mercedes-ortiz-dilone",
  "lia-ynocencia-diaz-santana",
  "julito-fulcar-encarnacion",
  "jonhson-encarnacion-diaz",
  "eduard-alexis-espiritusanto-castillo",
  "casimiro-antonio-marte-familia",
  "aracelis-villanueva-figueroa",
  "alexis-victoria-yeb",
] as const;

for (const id of electoralReformSponsors) {
  (verifiedSenatorInitiatives[id] ??= []).push({
    number: "05432-2024-2028-CD",
    title: "Proyecto de ley que deroga artículos de la Ley 20-23 Orgánica del Régimen Electoral y deroga la Ley 15-19",
    role: "Coproponente en el Senado",
    status: "approved_senate",
    introducedAt: "04/03/2026",
    sourceUrl: "https://camaradediputados.gob.do/download/1936/2026-plo-ordenes-del-dia-conocidos-por-el-pleno/27724/sesion-06-del-miercoles-18-de-marzo-de-2026.pdf",
  });
}

for (const id of ["alexis-victoria-yeb", "ramon-rogelio-genao-duran", "felix-ramon-bautista-rosario"] as const) {
  (verifiedSenatorInitiatives[id] ??= []).push({
    title: "Proyecto de ley que crea la Historia Clínica Electrónica y su Registro",
    role: "Proponente",
    status: "committee",
    sourceUrl: "https://www.senadord.gob.do/comision-de-salud-publica-continua-analisis-del-proyecto-para-la-creacion-de-la-historia-clinica-electronica-y-su-registro/",
  });
}
