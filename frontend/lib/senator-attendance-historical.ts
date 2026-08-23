export type HistoricalSenatorAttendance = {
  period: string;
  plenarySessions?: number;
  attended?: number;
  excused?: number;
  unjustifiedAbsences?: number;
  presenceRate: number;
  excusedRate?: number;
  absenceRate?: number;
  sourceUrl: string;
  sourceLabel: string;
  methodologyNote?: string;
};

/**
 * Historical attendance baselines from the prior constitutional period.
 * These records are intentionally kept separate from the 2024-2028 current-term
 * ranking so the OED can show continuity without mixing incomparable periods.
 */
export const historicalSenatorAttendance: Record<string, HistoricalSenatorAttendance[]> = {
  "santiago-jose-zorrilla": [
    {
      period: "2020-2024 (corte abril 2024)",
      plenarySessions: 207,
      attended: 181,
      presenceRate: 87.4,
      absenceRate: 12.6,
      sourceUrl: "https://listindiario.com/elecciones-generales-2024/20240520/asi-desempeno-santiago-zorrilla-senado-puesto-ocupara-cuatro-anos-mas_809153/amp.html",
      sourceLabel: "Listín Diario · extracción de registros del Senado 2020-2024",
      methodologyNote: "181 presencias de 207 sesiones; 26 faltas. Se conserva como línea base histórica y no se mezcla con el ranking 2024-2028.",
    },
  ],
  "ramon-rogelio-genao-duran": [
    {
      period: "2020-2024 (corte abril 2024)",
      plenarySessions: 207,
      attended: 194,
      presenceRate: 93.7,
      absenceRate: 6.3,
      sourceUrl: "https://listindiario.com/elecciones-generales-2024/20240521/asi-desempeno-ramon-rogelio-genao-senador-vega_809282.html",
      sourceLabel: "Listín Diario · extracción de registros del Senado 2020-2024",
      methodologyNote: "194 presencias y 13 faltas en 207 sesiones. Para 2025 existe además evidencia de que solo faltó a una sesión en el corte 27 feb.-5 ago., pero ese registro se mantiene fuera del porcentaje hasta cerrar el denominador exacto del período.",
    },
  ],
  "alexis-victoria-yeb": [
    {
      period: "2020-2024 (corte abril 2024)",
      plenarySessions: 207,
      attended: 182,
      presenceRate: 87.9,
      absenceRate: 12.1,
      sourceUrl: "https://listindiario.com/elecciones-generales-2024/20240521/asi-desempeno-alexis-victoria-yeb-senado-puesto-repite-2024-2028_809286/amp.html",
      sourceLabel: "Listín Diario · extracción de registros del Senado 2020-2024",
      methodologyNote: "182 presencias de 207 sesiones; 25 faltas. En 2025 aparecen 29 ausencias en pases de lista, pero no se convierten a porcentaje de sesiones porque son dos pases por sesión.",
    },
  ],
  "antonio-manuel-taveras-guzman": [
    {
      period: "2020-2024 (corte julio 2024)",
      presenceRate: 90,
      excusedRate: 9,
      absenceRate: 1,
      sourceUrl: "https://noticiassin.com/antonio-taveras-guzman-detalla-su-record-de-asistencia-y-ausencias-en-el-senado/",
      sourceLabel: "Noticias SIN · estadísticas atribuidas a la División de Relatoría, Asistencia y Votaciones del Senado",
      methodologyNote: "El registro divulgado por el senador, atribuido a la división técnica del Senado, reporta 90% de asistencia, 9% de excusas y 1% de ausencias. Es línea base del período anterior, no dato del ranking 2024-2028.",
    },
  ],
};
