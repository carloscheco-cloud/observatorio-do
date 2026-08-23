export type SenatorAttendanceEvidence = {
  period: string;
  metric: string;
  value: string;
  note: string;
  sourceUrl: string;
};

/**
 * Partial attendance evidence that is useful for transparency but must not be
 * converted into a plenary attendance percentage until the denominator and
 * measurement unit are fully comparable with the OED's session-based metric.
 */
export const senatorAttendanceEvidence: Record<string, SenatorAttendanceEvidence[]> = {
  "ramon-rogelio-genao-duran": [
    {
      period: "27 feb. – 5 ago. 2025",
      metric: "Sesiones ausente",
      value: "1",
      note: "La revisión periodística de las actas del Senado identifica solo una sesión ausente en el corte. El OED no publica todavía un porcentaje porque la fuente no expone en el mismo registro el total de sesiones comparables.",
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/26/tres-legisladores-del-prm-tienen-record-de-inasistencias-al-senado/3223892",
    },
  ],
  "alexis-victoria-yeb": [
    {
      period: "27 feb. – 5 ago. 2025",
      metric: "Pases de lista ausente",
      value: "29",
      note: "El Senado pasa lista dos veces por sesión. Por eso 29 pases de lista no equivalen automáticamente a 29 sesiones ausentes y no se convierten aún en porcentaje de plenarias.",
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/26/tres-legisladores-del-prm-tienen-record-de-inasistencias-al-senado/3223892",
    },
  ],
  "antonio-manuel-taveras-guzman": [
    {
      period: "27 feb. – 5 ago. 2025",
      metric: "Excusas registradas en pases de lista",
      value: "22",
      note: "La fuente agrega excusas registradas durante los dos pases de lista por sesión. Se conserva como evidencia parcial hasta cerrar el denominador de sesiones y permanencia.",
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/26/tres-legisladores-del-prm-tienen-record-de-inasistencias-al-senado/3223892",
    },
  ],
  "gustavo-lara-salazar": [
    {
      period: "29 abr. 2025",
      metric: "Ausencia observada en acta",
      value: "1 sesión identificada",
      note: "La revisión de las actas señala que ese día no asistió aunque su ausencia no fue leída públicamente al inicio de la sesión. Es evidencia puntual, no un porcentaje acumulado.",
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/26/tres-legisladores-del-prm-tienen-record-de-inasistencias-al-senado/3223892",
    },
  ],
  "rafael-baron-duluc-rijo": [
    {
      period: "29 abr. 2025",
      metric: "Ausencia observada en acta",
      value: "1 sesión identificada",
      note: "La revisión de las actas señala que ese día no asistió aunque su ausencia no fue leída públicamente al inicio de la sesión. Es evidencia puntual, no un porcentaje acumulado.",
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/26/tres-legisladores-del-prm-tienen-record-de-inasistencias-al-senado/3223892",
    },
  ],
};
