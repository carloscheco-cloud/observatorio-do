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

const may2026Source = "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026";

export const senatorCommitteeSummary: Record<string, SenatorCommitteeSummary[]> = {};

for (const [id, records] of Object.entries(verifiedSenatorCommissionAttendance)) {
  const present = records.filter((record) => record.status === "present");
  senatorCommitteeSummary[id] = [{
    period: "mayo 2026 · registros ya verificados",
    verifiedMeetings: present.length,
    verifiedMinutes: present.reduce((total, record) => total + (record.durationMinutes ?? 0), 0),
    sourceUrl: may2026Source,
    note: "Conteo de reuniones individualmente verificadas en el informe mensual. No se presenta como porcentaje del total de comisiones hasta cerrar el denominador completo de convocatorias asignadas.",
  }];
}

senatorCommitteeSummary["santiago-jose-zorrilla"] = [{
  period: "2020-2024 (corte histórico)",
  meetingsCalled: 587,
  meetingsAttended: 252,
  attendanceRate: 42.93,
  sourceUrl: "https://listindiario.com/elecciones-generales-2024/20240520/asi-desempeno-santiago-zorrilla-senado-puesto-ocupara-cuatro-anos-mas_809153/amp.html",
  note: "Histórico del período anterior; no debe mezclarse con el ranking de comisiones 2024-2028.",
}];

senatorCommitteeSummary["ramon-rogelio-genao-duran"] = [{
  period: "2020-2024 (corte histórico)",
  meetingsCalled: 923,
  meetingsAttended: 277,
  attendanceRate: 30.01,
  sourceUrl: "https://listindiario.com/elecciones-generales-2024/20240521/asi-desempeno-ramon-rogelio-genao-senador-vega_809282.html",
  note: "Histórico del período anterior; no debe mezclarse con el ranking de comisiones 2024-2028.",
}];

senatorCommitteeSummary["alexis-victoria-yeb"] = [{
  period: "2020-2024 (corte histórico)",
  meetingsCalled: 744,
  meetingsAttended: 495,
  attendanceRate: 66.53,
  sourceUrl: "https://listindiario.com/elecciones-generales-2024/20240521/asi-desempeno-alexis-victoria-yeb-senado-puesto-repite-2024-2028_809286/amp.html",
  note: "Histórico del período anterior; no debe mezclarse con el ranking de comisiones 2024-2028.",
}];

senatorCommitteeSummary["julito-fulcar-encarnacion"] = [{
  period: "2024-2025 · informe de gestión",
  attendanceRate: 71,
  sourceUrl: "https://www.senadord.gob.do/",
  note: "El informe de gestión reseña 71% de presencia, 18% de excusas y 11% de ausencias en comisiones. Mantener separado hasta enlazar el documento específico en el OED.",
}];
