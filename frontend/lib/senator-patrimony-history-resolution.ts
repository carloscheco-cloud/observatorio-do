export type SenatorPatrimonyHistoryResolution = {
  status: "antecedent_found" | "no_prior_declaration_identified";
  period?: string;
  priorOffice?: string;
  sourceUrl: string;
  note: string;
};

/**
 * Resolución documental para senadores que no tenían todavía una serie histórica
 * dentro de senator-patrimony-history.ts. No inventa montos: identifica el cargo
 * público previo que permite localizar declaraciones anteriores o deja constancia
 * de que el expediente oficial consultado no muestra un antecedente declarativo
 * público anterior al Senado 2024-2028.
 */
export const senatorPatrimonyHistoryResolution: Record<string, SenatorPatrimonyHistoryResolution> = {
  "omar-leonel-fernandez-dominguez": {
    status: "antecedent_found",
    period: "2020-2024",
    priorOffice: "Diputado por la circunscripción 1 del Distrito Nacional",
    sourceUrl: "https://www.senadord.gob.do/provincia/distrito-nacional/",
    note: "El perfil oficial confirma su paso por la Cámara de Diputados antes de asumir el Senado en 2024. Ese período constituye el punto de búsqueda para su declaración jurada anterior.",
  },
  "carlos-manuel-gomez-urena": {
    status: "antecedent_found",
    period: "2020-2024",
    priorOffice: "Senador por Espaillat",
    sourceUrl: "https://www.senadord.gob.do/provincia/espaillat/",
    note: "El perfil oficial confirma que fue electo senador en 2020 y reelecto en 2024. Debe existir una comparación declarativa del período anterior si el formulario fue depositado y publicado.",
  },
  "dagoberto-rodriguez-adames": {
    status: "antecedent_found",
    period: "1994-2006",
    priorOffice: "Senador por Independencia",
    sourceUrl: "https://www.senadord.gob.do/provincia/independencia/",
    note: "El perfil oficial documenta tres períodos senatoriales previos: 1994-1998, 1998-2002 y 2002-2006. El OED conserva este antecedente para rastrear declaraciones patrimoniales históricas.",
  },
  "eduard-alexis-espiritusanto-castillo": {
    status: "antecedent_found",
    period: "2020-2024",
    priorOffice: "Diputado por La Romana",
    sourceUrl: "https://www.senadord.gob.do/provincia/la-romana/",
    note: "El perfil oficial confirma que fue diputado electo en 2020 antes de pasar al Senado en 2024.",
  },
  "bernardo-aleman-rodriguez": {
    status: "antecedent_found",
    period: "1998-2006; 2016-2020",
    priorOffice: "Senador por Monte Cristi y posteriormente diputado",
    sourceUrl: "https://www.senadord.gob.do/provincia/montecristi/",
    note: "El perfil oficial documenta los períodos senatoriales 1998-2002 y 2002-2006, además de la diputación 2016-2020. Son puntos históricos para rastrear declaraciones patrimoniales.",
  },
  "pedro-antonio-tineo-nunez": {
    status: "antecedent_found",
    priorOffice: "Diputado por Monte Plata",
    sourceUrl: "https://www.senadord.gob.do/provincia/monte-plata/",
    note: "El perfil oficial confirma desempeño previo en la Cámara de Diputados, incluyendo presidencia de la Comisión Permanente de Administración Pública. Falta recuperar la declaración correspondiente a ese cargo.",
  },
  "aracelis-villanueva-figueroa": {
    status: "antecedent_found",
    period: "2020-2024",
    priorOffice: "Gobernadora de San Pedro de Macorís; previamente regidora",
    sourceUrl: "https://www.senadord.gob.do/provincia/san-pedro-de-macoris/",
    note: "El perfil oficial confirma que fue regidora durante dos períodos y gobernadora provincial 2020-2024 antes de asumir el Senado.",
  },
  "casimiro-antonio-marte-familia": {
    status: "antecedent_found",
    period: "2020-2024",
    priorOffice: "Senador por Santiago Rodríguez",
    sourceUrl: "https://www.senadord.gob.do/provincia/santiago-rodriguez/",
    note: "El perfil oficial confirma que fue senador 2020-2024 y reelecto 2024-2028. Ese período debe usarse para localizar su declaración anterior comparable.",
  },
  "andres-guillermo-lama-perez": {
    status: "no_prior_declaration_identified",
    period: "antes de 2024",
    sourceUrl: "https://www.senadord.gob.do/provincia/bahoruco/",
    note: "El perfil oficial presenta 2024 como su elección al Senado y describe trayectoria principalmente empresarial y partidaria. El OED no ha identificado todavía un cargo público previo con declaración jurada obligatoria publicada.",
  },
  "jonhson-encarnacion-diaz": {
    status: "no_prior_declaration_identified",
    period: "antes de 2024",
    sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43670/jonhson-encarnacion-diaz.pdf",
    note: "La DJP-42652 está tipificada como INICIO EN EL CARGO el 16-08-2024. El expediente consultado no identifica una declaración anterior del declarante.",
  },
  "secundino-velazquez-pimentel": {
    status: "no_prior_declaration_identified",
    period: "antes de 2024",
    sourceUrl: "https://www.senadord.gob.do/provincia/pedernales/",
    note: "El perfil oficial señala que fue candidato en 2016 y 2020 y resultó electo senador por primera vez en 2024. No se ha identificado un cargo público previo con declaración jurada obligatoria publicada.",
  },
};
