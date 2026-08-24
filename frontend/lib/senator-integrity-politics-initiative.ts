import type { SenatorInitiative } from "@/lib/senate-observation";

const sourceUrl = "https://www.senadord.gob.do/comision-especial-socializa-con-representantes-del-prm-iniciativa-que-busca-modificar-ley-de-partidos-politicos/";

const sponsorIds = [
  "ricardo-de-los-santos-polanco",
  "moises-ayala-perez",
  "antonio-manuel-taveras-guzman",
  "milciades-aneudy-ortiz-sajiun",
  "alexis-victoria-yeb",
  "andres-guillermo-lama-perez",
  "aracelis-villanueva-figueroa",
  "bernardo-aleman-rodriguez",
  "carlos-manuel-gomez-urena",
  "cristobal-venerado-castillo-liriano",
  "ginnette-altagracia-bournigal",
  "daniel-enrique-rivera-reyes",
  "dagoberto-rodriguez-adames",
  "franklin-martin-romero-morillo",
  "gustavo-lara-salazar",
  "julito-fulcar-encarnacion",
  "hector-elpidio-acosta-restituyo",
  "jonhson-encarnacion-diaz",
  "lia-ynocencia-diaz-santana",
  "pedro-antonio-tineo-nunez",
  "rafael-baron-duluc-rijo",
  "maria-mercedes-ortiz-dilone",
  "odalis-rafael-rodriguez-rodriguez",
  "santiago-jose-zorrilla",
  "manuel-maria-rodriguez-ortega",
  "secundino-velazquez-pimentel",
  "pedro-manuel-catrain-bonilla",
] as const;

const initiative: SenatorInitiative = {
  title: "Proyecto de ley sobre integridad, control del financiamiento y prevención de la infiltración de personas y recursos vinculados a actividades ilícitas en la política",
  role: "Acogente / impulsor según listado oficial del Senado",
  status: "committee",
  sourceUrl,
};

export const senatorIntegrityPoliticsInitiatives: Record<string, SenatorInitiative[]> = Object.fromEntries(
  sponsorIds.map((id) => [id, [initiative]])
);
