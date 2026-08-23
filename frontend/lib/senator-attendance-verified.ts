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
};

/**
 * Attendance is added only when an identifiable 2024-2028 Senate source
 * publishes either the exact roll-up or explicit percentages. Excused absence
 * is kept separate from absence without excuse.
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
    },
  ],
};
