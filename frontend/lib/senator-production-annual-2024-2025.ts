export type SenatorAnnualProductionMetric = {
  period: string;
  initiativesIntroduced: number;
  sourceUrl: string;
  sourceLabel: string;
  note?: string;
};

/**
 * Conteos publicados para el año legislativo completo 16 ago. 2024–26 jul. 2025.
 * Esta serie NO se mezcla matemáticamente con el corte corto 27 feb.–26 jul. 2025.
 */
export const senatorAnnualProduction20242025: Record<string, SenatorAnnualProductionMetric> = {
  "cristobal-venerado-castillo-liriano": { period: "16 ago. 2024 – 26 jul. 2025", initiativesIntroduced: 105, sourceUrl: "https://www.elcaribe.com.do/panorama/senador-cristobal-castillo-encabeza-listado-de-iniciativas-en-el-congreso-2024-2025/", sourceLabel: "El Caribe · balance año legislativo 2024-2025", note: "La fuente desglosa 49 resoluciones y 56 proyectos de ley." },
  "felix-ramon-bautista-rosario": { period: "16 ago. 2024 – 26 jul. 2025", initiativesIntroduced: 69, sourceUrl: "https://www.elcaribe.com.do/panorama/senador-cristobal-castillo-encabeza-listado-de-iniciativas-en-el-congreso-2024-2025/", sourceLabel: "El Caribe · balance año legislativo 2024-2025" },
  "rafael-baron-duluc-rijo": { period: "16 ago. 2024 – 26 jul. 2025", initiativesIntroduced: 61, sourceUrl: "https://www.elcaribe.com.do/panorama/senador-cristobal-castillo-encabeza-listado-de-iniciativas-en-el-congreso-2024-2025/", sourceLabel: "El Caribe · balance año legislativo 2024-2025" },
  "santiago-jose-zorrilla": { period: "16 ago. 2024 – 26 jul. 2025", initiativesIntroduced: 53, sourceUrl: "https://www.elcaribe.com.do/panorama/senador-cristobal-castillo-encabeza-listado-de-iniciativas-en-el-congreso-2024-2025/", sourceLabel: "El Caribe · balance año legislativo 2024-2025" },
  "maria-mercedes-ortiz-dilone": { period: "16 ago. 2024 – 26 jul. 2025", initiativesIntroduced: 42, sourceUrl: "https://www.elcaribe.com.do/panorama/senador-cristobal-castillo-encabeza-listado-de-iniciativas-en-el-congreso-2024-2025/", sourceLabel: "El Caribe · balance año legislativo 2024-2025" },
  "eduard-alexis-espiritusanto-castillo": { period: "16 ago. 2024 – 26 jul. 2025", initiativesIntroduced: 41, sourceUrl: "https://www.elcaribe.com.do/panorama/senador-cristobal-castillo-encabeza-listado-de-iniciativas-en-el-congreso-2024-2025/", sourceLabel: "El Caribe · balance año legislativo 2024-2025" },
  "daniel-enrique-rivera-reyes": { period: "16 ago. 2024 – 26 jul. 2025", initiativesIntroduced: 40, sourceUrl: "https://www.elcaribe.com.do/panorama/senador-cristobal-castillo-encabeza-listado-de-iniciativas-en-el-congreso-2024-2025/", sourceLabel: "El Caribe · balance año legislativo 2024-2025" },
  "alexis-victoria-yeb": { period: "16 ago. 2024 – 26 jul. 2025", initiativesIntroduced: 33, sourceUrl: "https://www.elcaribe.com.do/panorama/senador-cristobal-castillo-encabeza-listado-de-iniciativas-en-el-congreso-2024-2025/", sourceLabel: "El Caribe · balance año legislativo 2024-2025" },
  "franklin-martin-romero-morillo": { period: "16 ago. 2024 – 26 jul. 2025", initiativesIntroduced: 30, sourceUrl: "https://www.elcaribe.com.do/panorama/senador-cristobal-castillo-encabeza-listado-de-iniciativas-en-el-congreso-2024-2025/", sourceLabel: "El Caribe · balance año legislativo 2024-2025" },
};
