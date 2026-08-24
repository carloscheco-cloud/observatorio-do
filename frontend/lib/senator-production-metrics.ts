export type SenatorProductionMetric = {
  period: string;
  projectsIntroduced: number;
  sourceUrl: string;
  sourceLabel: string;
  note?: string;
};

/** Comparable project counts for the first ordinary 2025 legislature: 27 Feb–26 Jul 2025. */
export const senatorProductionMetrics: Record<string, SenatorProductionMetric> = {
  "cristobal-venerado-castillo-liriano": { period: "27 feb. – 26 jul. 2025", projectsIntroduced: 39, sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/16/como-concluyo-la-pasada-legislatura-senatorial/3214742", sourceLabel: "Diario Libre · consulta al Sistema de Información Legislativa" },
  "felix-ramon-bautista-rosario": { period: "27 feb. – 26 jul. 2025", projectsIntroduced: 28, sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/16/como-concluyo-la-pasada-legislatura-senatorial/3214742", sourceLabel: "Diario Libre · consulta al Sistema de Información Legislativa" },
  "rafael-baron-duluc-rijo": { period: "27 feb. – 26 jul. 2025", projectsIntroduced: 25, sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/16/como-concluyo-la-pasada-legislatura-senatorial/3214742", sourceLabel: "Diario Libre · consulta al Sistema de Información Legislativa" },
  "omar-leonel-fernandez-dominguez": { period: "27 feb. – 26 jul. 2025", projectsIntroduced: 11, sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/16/como-concluyo-la-pasada-legislatura-senatorial/3214742", sourceLabel: "Diario Libre · consulta al Sistema de Información Legislativa" },
  "daniel-enrique-rivera-reyes": { period: "27 feb. – 26 jul. 2025", projectsIntroduced: 5, sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/16/como-concluyo-la-pasada-legislatura-senatorial/3214742", sourceLabel: "Diario Libre · consulta al Sistema de Información Legislativa" },
  "gustavo-lara-salazar": { period: "27 feb. – 26 jul. 2025", projectsIntroduced: 2, sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/16/como-concluyo-la-pasada-legislatura-senatorial/3214742", sourceLabel: "Diario Libre · consulta al Sistema de Información Legislativa" },
  "manuel-maria-rodriguez-ortega": { period: "27 feb. – 26 jul. 2025", projectsIntroduced: 1, sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/16/como-concluyo-la-pasada-legislatura-senatorial/3214742", sourceLabel: "Diario Libre · consulta al Sistema de Información Legislativa", note: "La fuente identifica una iniciativa sobre agua potable y saneamiento." },
  "secundino-velazquez-pimentel": { period: "27 feb. – 26 jul. 2025", projectsIntroduced: 1, sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/16/como-concluyo-la-pasada-legislatura-senatorial/3214742", sourceLabel: "Diario Libre · consulta al Sistema de Información Legislativa", note: "La fuente identifica como única propuesta declarar Pedernales provincia ecoturística." },
  "bernardo-aleman-rodriguez": { period: "27 feb. – 26 jul. 2025", projectsIntroduced: 0, sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/16/como-concluyo-la-pasada-legislatura-senatorial/3214742", sourceLabel: "Diario Libre · consulta al Sistema de Información Legislativa" },
};

export const productionUniverse2025 = { period: "27 feb. – 26 jul. 2025", totalProjects: 256 };
