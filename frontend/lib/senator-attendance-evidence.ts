export type SenatorAttendanceEvidence = {
  period: string;
  metric: string;
  value: string;
  note: string;
  sourceUrl: string;
};

/**
 * Evidencia de asistencia útil para transparencia que NO debe convertirse en
 * porcentaje de plenarias mientras el denominador o la unidad de medición no
 * sea plenamente comparable. Los pases de lista tampoco equivalen de forma
 * automática a sesiones completas porque el Senado pasa lista al inicio y al final.
 */
export const senatorAttendanceEvidence: Record<string, SenatorAttendanceEvidence[]> = {
  "moises-ayala-perez": [{
    period: "18 dic. 2025",
    metric: "Presencia documentada",
    value: "Presente en primer pase de lista",
    note: "El acta oficial núm. 0095 lo registra presente al inicio. Evidencia puntual; no sustituye un porcentaje acumulado del período.",
    sourceUrl: "https://memoriahistorica.senadord.gob.do/server/api/core/bitstreams/043d4ee2-c595-496f-8a85-39e4b53815fc/content",
  }],
  "santiago-jose-zorrilla": [{
    period: "18 dic. 2025",
    metric: "Presencia documentada",
    value: "Presente en primer pase de lista",
    note: "El acta oficial núm. 0095 lo registra presente al inicio. El OED conserva esta evidencia puntual separada de cualquier porcentaje acumulado.",
    sourceUrl: "https://memoriahistorica.senadord.gob.do/server/api/core/bitstreams/043d4ee2-c595-496f-8a85-39e4b53815fc/content",
  }],
  "carlos-manuel-gomez-urena": [{
    period: "18 dic. 2025",
    metric: "Presencia documentada",
    value: "Presente en primer pase de lista",
    note: "El acta oficial núm. 0095 lo registra presente al inicio de la sesión. No se convierte en tasa acumulada sin revisar todas las actas del corte.",
    sourceUrl: "https://memoriahistorica.senadord.gob.do/server/api/core/bitstreams/043d4ee2-c595-496f-8a85-39e4b53815fc/content",
  }],
  "cristobal-venerado-castillo-liriano": [{
    period: "18 dic. 2025",
    metric: "Presencia documentada",
    value: "Presente en primer pase de lista",
    note: "El acta oficial núm. 0095 lo registra presente al inicio. Es evidencia puntual y no un porcentaje del período.",
    sourceUrl: "https://memoriahistorica.senadord.gob.do/server/api/core/bitstreams/043d4ee2-c595-496f-8a85-39e4b53815fc/content",
  }],
  "pedro-manuel-catrain-bonilla": [{
    period: "18 dic. 2025",
    metric: "Excusa formal",
    value: "1 sesión identificada",
    note: "El acta oficial núm. 0095 lo registra ausente con excusa legítima y reproduce la correspondencia formal remitida al presidente del Senado.",
    sourceUrl: "https://memoriahistorica.senadord.gob.do/server/api/core/bitstreams/043d4ee2-c595-496f-8a85-39e4b53815fc/content",
  }],
  "milciades-aneudy-ortiz-sajiun": [{
    period: "18 dic. 2025",
    metric: "Presencia documentada",
    value: "Presente en primer pase de lista",
    note: "El acta oficial núm. 0095 lo registra presente al inicio. Evidencia puntual pendiente de consolidación para el período completo.",
    sourceUrl: "https://memoriahistorica.senadord.gob.do/server/api/core/bitstreams/043d4ee2-c595-496f-8a85-39e4b53815fc/content",
  }],
  "aracelis-villanueva-figueroa": [{
    period: "18 dic. 2025",
    metric: "Incorporación después del quórum",
    value: "12:10 p. m.",
    note: "El acta oficial núm. 0095 registra que se incorporó a las 12:10 p. m. después de comprobado el quórum. No se interpreta como ausencia total de la sesión.",
    sourceUrl: "https://memoriahistorica.senadord.gob.do/server/api/core/bitstreams/043d4ee2-c595-496f-8a85-39e4b53815fc/content",
  }],
  "ramon-rogelio-genao-duran": [{
    period: "27 feb. – 5 ago. 2025",
    metric: "Sesiones ausente",
    value: "1",
    note: "La revisión periodística de las actas del Senado identifica solo una sesión ausente en el corte. El OED no publica todavía un porcentaje porque la fuente no expone en el mismo registro el total de sesiones comparables.",
    sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/26/tres-legisladores-del-prm-tienen-record-de-inasistencias-al-senado/3223892",
  }],
  "alexis-victoria-yeb": [{
    period: "27 feb. – 5 ago. 2025",
    metric: "Pases de lista ausente",
    value: "29",
    note: "El Senado pasa lista dos veces por sesión. Por eso 29 pases de lista no equivalen automáticamente a 29 sesiones ausentes y no se convierten aún en porcentaje de plenarias.",
    sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/26/tres-legisladores-del-prm-tienen-record-de-inasistencias-al-senado/3223892",
  }],
  "antonio-manuel-taveras-guzman": [{
    period: "27 feb. – 5 ago. 2025",
    metric: "Excusas registradas en pases de lista",
    value: "22",
    note: "La fuente agrega excusas registradas durante los dos pases de lista por sesión. Se conserva como evidencia parcial hasta cerrar el denominador de sesiones y permanencia.",
    sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/26/tres-legisladores-del-prm-tienen-record-de-inasistencias-al-senado/3223892",
  }],
  "gustavo-lara-salazar": [{
    period: "29 abr. 2025",
    metric: "Ausencia observada en acta",
    value: "1 sesión identificada",
    note: "La revisión de las actas señala que ese día no asistió aunque su ausencia no fue leída públicamente al inicio de la sesión. Es evidencia puntual, no un porcentaje acumulado.",
    sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/26/tres-legisladores-del-prm-tienen-record-de-inasistencias-al-senado/3223892",
  }],
  "rafael-baron-duluc-rijo": [{
    period: "29 abr. 2025",
    metric: "Ausencia observada en acta",
    value: "1 sesión identificada",
    note: "La revisión de las actas señala que ese día no asistió aunque su ausencia no fue leída públicamente al inicio de la sesión. Es evidencia puntual, no un porcentaje acumulado.",
    sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/26/tres-legisladores-del-prm-tienen-record-de-inasistencias-al-senado/3223892",
  }],
};
