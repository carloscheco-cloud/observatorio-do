import { verifiedSenatorCommissionAttendance } from "@/lib/senator-commission-attendance-verified";

export type SenatorCommitteeSummary = {
  period: string;
  verifiedMeetings?: number;
  verifiedMinutes?: number;
  attendanceRate?: number;
  meetingsCalled?: number;
  meetingsAttended?: number;
  sourceUrl: string;
  note: string;
};

const monthNames: Record<string, string> = {
  "01": "enero", "02": "febrero", "03": "marzo", "04": "abril",
  "05": "mayo", "06": "junio", "07": "julio", "08": "agosto",
  "09": "septiembre", "10": "octubre", "11": "noviembre", "12": "diciembre",
};

export const senatorCommitteeSummary: Record<string, SenatorCommitteeSummary[]> = {};

for (const [id, records] of Object.entries(verifiedSenatorCommissionAttendance)) {
  const grouped = new Map<string, typeof records>();
  for (const record of records) {
    const key = record.date.slice(0, 7);
    const current = grouped.get(key) ?? [];
    current.push(record);
    grouped.set(key, current);
  }

  senatorCommitteeSummary[id] = [...grouped.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([periodKey, periodRecords]) => {
      const present = periodRecords.filter((record) => record.status === "present");
      const [year, month] = periodKey.split("-");
      return {
        period: `${monthNames[month] ?? month} ${year} · registros verificados`,
        verifiedMeetings: present.length,
        verifiedMinutes: present.reduce((total, record) => total + (record.durationMinutes ?? 0), 0),
        sourceUrl: periodRecords[0]?.sourceUrl ?? "https://www.senadord.gob.do/comisiones/",
        note: "Conteo de reuniones individualmente verificadas para este mes. No se presenta como porcentaje del total de comisiones hasta cerrar el denominador completo de convocatorias que correspondían al senador.",
      };
    });
}

senatorCommitteeSummary["santiago-jose-zorrilla"] = [
  ...(senatorCommitteeSummary["santiago-jose-zorrilla"] ?? []),
  {
    period: "2020-2024 (corte histórico)",
    meetingsCalled: 587,
    meetingsAttended: 252,
    attendanceRate: 42.93,
    sourceUrl: "https://listindiario.com/elecciones-generales-2024/20240520/asi-desempeno-santiago-zorrilla-senado-puesto-ocupara-cuatro-anos-mas_809153/amp.html",
    note: "Histórico del período anterior; no debe mezclarse con el ranking de comisiones 2024-2028.",
  },
];

senatorCommitteeSummary["ramon-rogelio-genao-duran"] = [
  ...(senatorCommitteeSummary["ramon-rogelio-genao-duran"] ?? []),
  {
    period: "2020-2024 (corte histórico)",
    meetingsCalled: 923,
    meetingsAttended: 277,
    attendanceRate: 30.01,
    sourceUrl: "https://listindiario.com/elecciones-generales-2024/20240521/asi-desempeno-ramon-rogelio-genao-senador-vega_809282.html",
    note: "Histórico del período anterior; no debe mezclarse con el ranking de comisiones 2024-2028.",
  },
];

senatorCommitteeSummary["alexis-victoria-yeb"] = [
  ...(senatorCommitteeSummary["alexis-victoria-yeb"] ?? []),
  {
    period: "2020-2024 (corte histórico)",
    meetingsCalled: 744,
    meetingsAttended: 495,
    attendanceRate: 66.53,
    sourceUrl: "https://listindiario.com/elecciones-generales-2024/20240521/asi-desempeno-alexis-victoria-yeb-senado-puesto-repite-2024-2028_809286/amp.html",
    note: "Histórico del período anterior; no debe mezclarse con el ranking de comisiones 2024-2028.",
  },
];

senatorCommitteeSummary["julito-fulcar-encarnacion"] = [
  ...(senatorCommitteeSummary["julito-fulcar-encarnacion"] ?? []),
  {
    period: "2024-2025 · informe de gestión",
    attendanceRate: 71,
    sourceUrl: "https://www.senadord.gob.do/",
    note: "El informe de gestión reseña 71% de presencia, 18% de excusas y 11% de ausencias en comisiones. Mantener separado hasta enlazar el documento específico en el OED.",
  },
];
