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

const dl2025 = "https://www.diariolibre.com/politica/congreso-nacional/2025/01/27/conozca-a-los-senadores-ausentes-de-las-sesiones/2979560";
const dl2026a = "https://www.diariolibre.com/politica/congreso-nacional/2026/02/06/legisladores-registran-altas-cifras-de-ausencia-a-sesiones/3427897";
const dl2026b = "https://www.diariolibre.com/politica/congreso-nacional/2026/02/17/cuatro-senadores-son-los-que-registran-menos-proyectos-en-su-labor/3438881";
const dl2026c = "https://www.diariolibre.com/politica/congreso-nacional/2026/08/12/los-senadores-se-escudaron-en-100-excusas-para-faltar-a-las-sesiones/3626113";

function row(
  period: string,
  plenarySessions: number | undefined,
  attended: number | undefined,
  excused: number | undefined,
  presenceRate: number,
  excusedRate: number,
  sourceUrl: string,
  methodologyNote: string,
): VerifiedSenatorAttendance {
  return {
    period,
    plenarySessions,
    attended,
    excused,
    unjustifiedAbsences: 0,
    presenceRate,
    excusedRate,
    absenceRate: 0,
    sourceUrl,
    sourceLabel: "Revisión documental basada en actas y registros de asistencia del Senado",
    methodologyNote,
  };
}

export const verifiedSenatorAttendance: Record<string, VerifiedSenatorAttendance[]> = {
  "lia-ynocencia-diaz-santana": [row("16 ago. 2025 – 12 ene. 2026", 24, 24, 0, 100, 0, dl2026a, "Asistencia perfecta en las 24 sesiones del período.")],
  "andres-guillermo-lama-perez": [row("27 feb. – 26 jul. 2026", 26, 26, 0, 100, 0, dl2026c, "Asistencia perfecta en las 26 sesiones revisadas.")],
  "manuel-maria-rodriguez-ortega": [row("16 ago. 2025 – 12 ene. 2026", 24, 21, 3, 87.5, 12.5, dl2026b, "Tres ausencias de 24 sesiones; la revisión general de las actas del período indica que las ausencias fueron sustentadas con justificación escrita.")],
  "omar-leonel-fernandez-dominguez": [row("16 ago. 2024 – 12 ene. 2025", 24, 17, 7, 70.8, 29.2, dl2025, "Siete faltas en 24 sesiones, registradas con excusa; 17 presencias calculadas por diferencia.")],
  "franklin-martin-romero-morillo": [row("16 ago. 2024 – 12 ene. 2025", 24, 15, 9, 62.5, 37.5, dl2025, "Nueve faltas en 24 sesiones, registradas con excusa; 15 presencias calculadas por diferencia.")],
  "jonhson-encarnacion-diaz": [row("16 ago. 2025 – 12 ene. 2026", 24, 22, 2, 91.7, 8.3, dl2026b, "Dos ausencias de 24 sesiones; la revisión general de las actas del período indica que las ausencias fueron sustentadas con justificación escrita.")],
  "maria-mercedes-ortiz-dilone": [row("27 feb. – 26 jul. 2026", 26, 26, 0, 100, 0, dl2026c, "Asistencia perfecta en las 26 sesiones revisadas.")],
  "dagoberto-rodriguez-adames": [row("27 feb. – 26 jul. 2026", 26, 26, 0, 100, 0, dl2026c, "Asistencia perfecta en las 26 sesiones revisadas.")],
  "eduard-alexis-espiritusanto-castillo": [row("16 ago. 2024 – 12 ene. 2025", 24, 18, 6, 75, 25, dl2025, "Seis faltas en 24 sesiones, registradas con excusa; 18 presencias calculadas por diferencia.")],
  "hector-elpidio-acosta-restituyo": [
    row("16 ago. 2025 – 12 ene. 2026", 24, 8, 16, 33.3, 66.7, dl2026a, "Dieciséis ausencias de 24 sesiones, todas justificadas. La fuente señala una situación de salud hecha pública."),
    row("27 feb. – 26 jul. 2026", 26, 16, 10, 61.5, 38.5, dl2026c, "Diez de las 26 sesiones figuran con excusa; ninguna ausencia injustificada registrada."),
  ],
  "bernardo-aleman-rodriguez": [row("16 ago. 2025 – 12 ene. 2026", 24, 14, 10, 58.3, 41.7, dl2026a, "Diez faltas de 24 sesiones, todas con excusa; 14 presencias calculadas por diferencia.")],
  "pedro-antonio-tineo-nunez": [row("16 ago. 2024 – 12 ene. 2025", 24, 15, 9, 62.5, 37.5, dl2025, "Nueve faltas en 24 sesiones, registradas con excusa; 15 presencias calculadas por diferencia.")],
  "secundino-velazquez-pimentel": [{
    period: "2024-2025",
    plenarySessions: 67,
    attended: 61,
    excused: 6,
    unjustifiedAbsences: 0,
    presenceRate: 91,
    excusedRate: 9,
    absenceRate: 0,
    sourceUrl: "https://cdnc.heyzine.com/files/uploaded/v3/dde740efa9deac1b2f6a844dca68328a4226b74e.pdf",
    sourceLabel: "Informe de Gestión Senatorial Pedernales 2024-2025 · Departamento de Elaboración de Actas",
    methodologyNote: "El informe consolida 67 sesiones/actas, 61 presencias, 6 excusas y 0 ausencias sin excusa.",
  }],
  "julito-fulcar-encarnacion": [{
    period: "2024-2025",
    presenceRate: 96,
    excusedRate: 4,
    absenceRate: 0,
    sourceUrl: "https://fliphtml5.com/qintr/wqwa/web-memoriasJulito-new/",
    sourceLabel: "Informe de Gestión Social y Legislativa 2024-2025 · Senador Julito Fulcar",
    methodologyNote: "El informe publica directamente 96% presencia, 4% excusas y 0% ausencias.",
  }],
  "ginnette-altagracia-bournigal": [row("27 feb. – 26 jul. 2026", 26, 18, 8, 69.2, 30.8, dl2026c, "Ocho de las 26 sesiones figuran con excusa; ninguna ausencia injustificada registrada.")],
  "felix-ramon-bautista-rosario": [row("27 feb. – 26 jul. 2026", 26, 15, 11, 57.7, 42.3, dl2026c, "Once de las 26 sesiones figuran con excusa; ninguna ausencia injustificada registrada.")],
  "ricardo-de-los-santos-polanco": [row("27 feb. – 26 jul. 2026", 26, 26, 0, 100, 0, dl2026c, "Asistencia perfecta en las 26 sesiones revisadas.")],
  "daniel-enrique-rivera-reyes": [row("27 feb. – 26 jul. 2026", 26, 26, 0, 100, 0, dl2026c, "Asistencia perfecta en las 26 sesiones revisadas.")],
  "casimiro-antonio-marte-familia": [row("27 feb. – 26 jul. 2026", 26, 26, 0, 100, 0, dl2026c, "La fuente identifica al senador como Antonio Marte; corresponde a Casimiro Antonio Marte Familia. Asistencia perfecta.")],
  "odalis-rafael-rodriguez-rodriguez": [row("27 feb. – 26 jul. 2026", 26, 26, 0, 100, 0, dl2026c, "Asistencia perfecta en las 26 sesiones revisadas.")],
};
