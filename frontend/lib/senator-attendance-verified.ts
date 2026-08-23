export type VerifiedSenatorAttendance = {
  period: string;
  plenarySessions?: number;
  attended?: number;
  excused?: number;
  unjustifiedAbsences?: number;
  presenceRate: number;
  excusedRate: number;
  absenceRate: number;
  sourceUrl: string;
  sourceLabel: string;
  methodologyNote?: string;
};

/**
 * Attendance is added only when an identifiable source based on Senate records
 * publishes either the exact roll-up or an explicit percentage. Excused absence
 * is kept separate from absence without excuse. We do not manufacture a
 * percentage from incomplete pass-of-list counts.
 */
export const verifiedSenatorAttendance: Record<string, VerifiedSenatorAttendance[]> = {
  "julito-fulcar-encarnacion": [
    {
      period: "2024-2025",
      presenceRate: 96,
      excusedRate: 4,
      absenceRate: 0,
      sourceUrl: "https://fliphtml5.com/qintr/wqwa/web-memoriasJulito-new/",
      sourceLabel: "Informe de Gestión Social y Legislativa 2024-2025 · Senador Julito Fulcar",
      methodologyNote: "El informe publica directamente los porcentajes de presencia, excusas y ausencias.",
    },
  ],
  "secundino-velazquez-pimentel": [
    {
      period: "2024-2025",
      plenarySessions: 67,
      attended: 61,
      excused: 6,
      unjustifiedAbsences: 0,
      presenceRate: 91,
      excusedRate: 9,
      absenceRate: 0,
      sourceUrl: "https://cdnc.heyzine.com/files/uploaded/v3/dde740efa9deac1b2f6a844dca68328a4226b74e.pdf",
      sourceLabel: "Informe de Gestión Senatorial Pedernales 2024-2025 · Departamento Elaboración de Actas",
      methodologyNote: "El informe oficial consolida 67 sesiones/actas, 61 presencias, 6 excusas y 0 ausencias.",
    },
  ],
  "ricardo-de-los-santos-polanco": [
    {
      period: "27 feb. – 5 ago. 2025",
      presenceRate: 100,
      excusedRate: 0,
      absenceRate: 0,
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/26/tres-legisladores-del-prm-tienen-record-de-inasistencias-al-senado/3223892",
      sourceLabel: "Diario Libre · revisión de listados oficiales de asistencia publicados por el Senado",
      methodologyNote: "La revisión reporta asistencia perfecta en ambos pases de lista durante todas las sesiones del período analizado.",
    },
    {
      period: "27 feb. – 26 jul. 2026",
      plenarySessions: 26,
      attended: 26,
      excused: 0,
      unjustifiedAbsences: 0,
      presenceRate: 100,
      excusedRate: 0,
      absenceRate: 0,
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2026/08/12/los-senadores-se-escudaron-en-100-excusas-para-faltar-a-las-sesiones/3626113",
      sourceLabel: "Diario Libre · revisión de las 26 actas de sesiones del Senado, legislatura feb.-jul. 2026",
      methodologyNote: "Asistencia perfecta en las 26 sesiones revisadas; ninguna ausencia injustificada registrada.",
    },
  ],
  "odalis-rafael-rodriguez-rodriguez": [
    {
      period: "27 feb. – 5 ago. 2025",
      presenceRate: 100,
      excusedRate: 0,
      absenceRate: 0,
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/26/tres-legisladores-del-prm-tienen-record-de-inasistencias-al-senado/3223892",
      sourceLabel: "Diario Libre · revisión de listados oficiales de asistencia publicados por el Senado",
      methodologyNote: "La revisión reporta asistencia perfecta en ambos pases de lista durante todas las sesiones del período analizado.",
    },
    {
      period: "27 feb. – 26 jul. 2026",
      plenarySessions: 26,
      attended: 26,
      excused: 0,
      unjustifiedAbsences: 0,
      presenceRate: 100,
      excusedRate: 0,
      absenceRate: 0,
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2026/08/12/los-senadores-se-escudaron-en-100-excusas-para-faltar-a-las-sesiones/3626113",
      sourceLabel: "Diario Libre · revisión de las 26 actas de sesiones del Senado, legislatura feb.-jul. 2026",
      methodologyNote: "Asistencia perfecta en las 26 sesiones revisadas; ninguna ausencia injustificada registrada.",
    },
  ],
  "dagoberto-rodriguez-adames": [
    {
      period: "27 feb. – 26 jul. 2026",
      plenarySessions: 26,
      attended: 26,
      excused: 0,
      unjustifiedAbsences: 0,
      presenceRate: 100,
      excusedRate: 0,
      absenceRate: 0,
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2026/08/12/los-senadores-se-escudaron-en-100-excusas-para-faltar-a-las-sesiones/3626113",
      sourceLabel: "Diario Libre · revisión de las 26 actas de sesiones del Senado, legislatura feb.-jul. 2026",
      methodologyNote: "Asistencia perfecta en las 26 sesiones revisadas.",
    },
  ],
  "casimiro-antonio-marte-familia": [
    {
      period: "27 feb. – 26 jul. 2026",
      plenarySessions: 26,
      attended: 26,
      excused: 0,
      unjustifiedAbsences: 0,
      presenceRate: 100,
      excusedRate: 0,
      absenceRate: 0,
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2026/08/12/los-senadores-se-escudaron-en-100-excusas-para-faltar-a-las-sesiones/3626113",
      sourceLabel: "Diario Libre · revisión de las 26 actas de sesiones del Senado, legislatura feb.-jul. 2026",
      methodologyNote: "La fuente identifica al senador de Santiago Rodríguez como Antonio Marte; corresponde a Casimiro Antonio Marte Familia en el roster vigente del OED. Asistencia perfecta en las 26 sesiones.",
    },
  ],
  "maria-mercedes-ortiz-dilone": [
    {
      period: "27 feb. – 26 jul. 2026",
      plenarySessions: 26,
      attended: 26,
      excused: 0,
      unjustifiedAbsences: 0,
      presenceRate: 100,
      excusedRate: 0,
      absenceRate: 0,
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2026/08/12/los-senadores-se-escudaron-en-100-excusas-para-faltar-a-las-sesiones/3626113",
      sourceLabel: "Diario Libre · revisión de las 26 actas de sesiones del Senado, legislatura feb.-jul. 2026",
      methodologyNote: "Asistencia perfecta en las 26 sesiones revisadas.",
    },
  ],
  "andres-guillermo-lama-perez": [
    {
      period: "27 feb. – 26 jul. 2026",
      plenarySessions: 26,
      attended: 26,
      excused: 0,
      unjustifiedAbsences: 0,
      presenceRate: 100,
      excusedRate: 0,
      absenceRate: 0,
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2026/08/12/los-senadores-se-escudaron-en-100-excusas-para-faltar-a-las-sesiones/3626113",
      sourceLabel: "Diario Libre · revisión de las 26 actas de sesiones del Senado, legislatura feb.-jul. 2026",
      methodologyNote: "Asistencia perfecta en las 26 sesiones revisadas.",
    },
  ],
  "daniel-enrique-rivera-reyes": [
    {
      period: "27 feb. – 26 jul. 2026",
      plenarySessions: 26,
      attended: 26,
      excused: 0,
      unjustifiedAbsences: 0,
      presenceRate: 100,
      excusedRate: 0,
      absenceRate: 0,
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2026/08/12/los-senadores-se-escudaron-en-100-excusas-para-faltar-a-las-sesiones/3626113",
      sourceLabel: "Diario Libre · revisión de las 26 actas de sesiones del Senado, legislatura feb.-jul. 2026",
      methodologyNote: "Asistencia perfecta en las 26 sesiones revisadas.",
    },
  ],
  "felix-ramon-bautista-rosario": [
    {
      period: "27 feb. – 26 jul. 2026",
      plenarySessions: 26,
      attended: 15,
      excused: 11,
      unjustifiedAbsences: 0,
      presenceRate: 57.7,
      excusedRate: 42.3,
      absenceRate: 0,
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2026/08/12/los-senadores-se-escudaron-en-100-excusas-para-faltar-a-las-sesiones/3626113",
      sourceLabel: "Diario Libre · revisión de las 26 actas de sesiones del Senado, legislatura feb.-jul. 2026",
      methodologyNote: "11 de las 26 sesiones figuran con excusa; ninguna ausencia fue registrada como injustificada.",
    },
  ],
  "hector-elpidio-acosta-restituyo": [
    {
      period: "27 feb. – 26 jul. 2026",
      plenarySessions: 26,
      attended: 16,
      excused: 10,
      unjustifiedAbsences: 0,
      presenceRate: 61.5,
      excusedRate: 38.5,
      absenceRate: 0,
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2026/08/12/los-senadores-se-escudaron-en-100-excusas-para-faltar-a-las-sesiones/3626113",
      sourceLabel: "Diario Libre · revisión de las 26 actas de sesiones del Senado, legislatura feb.-jul. 2026",
      methodologyNote: "10 de las 26 sesiones figuran con excusa; ninguna ausencia fue registrada como injustificada.",
    },
  ],
  "ginnette-altagracia-bournigal": [
    {
      period: "27 feb. – 26 jul. 2026",
      plenarySessions: 26,
      attended: 18,
      excused: 8,
      unjustifiedAbsences: 0,
      presenceRate: 69.2,
      excusedRate: 30.8,
      absenceRate: 0,
      sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2026/08/12/los-senadores-se-escudaron-en-100-excusas-para-faltar-a-las-sesiones/3626113",
      sourceLabel: "Diario Libre · revisión de las 26 actas de sesiones del Senado, legislatura feb.-jul. 2026",
      methodologyNote: "8 de las 26 sesiones figuran con excusa; ninguna ausencia fue registrada como injustificada.",
    },
  ],
};
