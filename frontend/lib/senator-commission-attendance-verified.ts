export type SenatorCommissionAttendanceRecord = {
  date: string;
  commission: string;
  status: "present" | "excused" | "absent" | "other_commission";
  arrival?: string;
  departure?: string;
  durationMinutes?: number;
  sourceUrl: string;
  note?: string;
};

/**
 * Verified committee-attendance records. These records are not converted into
 * an aggregate percentage unless the OED has the full denominator of meetings
 * for the senator's assigned commissions in the selected period.
 */
export const verifiedSenatorCommissionAttendance: Record<string, SenatorCommissionAttendanceRecord[]> = {
  "moises-ayala-perez": [
    {
      date: "2026-05-05",
      commission: "Comisión registrada en informe mensual del Senado",
      status: "present",
      arrival: "10:20",
      departure: "10:40",
      durationMinutes: 20,
      sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026",
      note: "El informe oficial registra llegada, salida y 20 minutos de presencia.",
    },
    {
      date: "2026-05-26",
      commission: "Asuntos Energéticos",
      status: "present",
      arrival: "10:00",
      departure: "10:50",
      durationMinutes: 50,
      sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026",
      note: "Presencia completa durante los 50 minutos de la reunión registrada.",
    },
  ],
  "gustavo-lara-salazar": [
    {
      date: "2026-05-06",
      commission: "Deportes",
      status: "present",
      arrival: "09:00",
      departure: "09:18",
      durationMinutes: 18,
      sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026",
      note: "Presencia durante la totalidad de la reunión registrada.",
    },
    {
      date: "2026-05-26",
      commission: "Asuntos Energéticos",
      status: "present",
      arrival: "10:05",
      departure: "10:50",
      durationMinutes: 45,
      sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026",
      note: "Llegó cinco minutos después del inicio y permaneció hasta el cierre.",
    },
    {
      date: "2026-05-27",
      commission: "Deportes",
      status: "present",
      arrival: "09:30",
      departure: "10:30",
      durationMinutes: 60,
      sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026",
      note: "Presencia completa durante una hora.",
    },
  ],
  "pedro-manuel-catrain-bonilla": [
    {
      date: "2026-05-19",
      commission: "Comisión Especial sobre integridad, control del financiamiento y prevención en la política · Exp. 01452",
      status: "present",
      arrival: "12:00",
      departure: "12:59",
      durationMinutes: 59,
      sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026",
      note: "Presencia durante la totalidad de la reunión registrada.",
    },
    {
      date: "2026-05-19",
      commission: "Reunión de comisión registrada en el informe mensual",
      status: "present",
      arrival: "10:40",
      departure: "11:26",
      durationMinutes: 46,
      sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026",
      note: "El informe oficial registra 46 minutos de presencia.",
    },
  ],
  "aracelis-villanueva-figueroa": [
    {
      date: "2026-05-12",
      commission: "Relaciones Exteriores y Cooperación Internacional",
      status: "present",
      arrival: "12:30",
      departure: "13:10",
      durationMinutes: 40,
      sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026",
      note: "Presencia completa durante los 40 minutos de la reunión.",
    },
    {
      date: "2026-05-19",
      commission: "Comisión Especial sobre integridad, control del financiamiento y prevención en la política · Exp. 01452",
      status: "present",
      arrival: "12:00",
      departure: "12:59",
      durationMinutes: 59,
      sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026",
      note: "Presencia durante la totalidad de la reunión registrada.",
    },
    {
      date: "2026-05-21",
      commission: "Asuntos de la Familia y Equidad de Género",
      status: "present",
      arrival: "10:00",
      departure: "11:45",
      durationMinutes: 105,
      sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026",
      note: "Presencia completa durante 1 hora y 45 minutos.",
    },
  ],
  "rafael-baron-duluc-rijo": [
    {
      date: "2026-05-05",
      commission: "Reunión de comisión registrada en informe mensual del Senado",
      status: "present",
      arrival: "10:00",
      departure: "10:40",
      durationMinutes: 40,
      sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026",
      note: "El informe oficial registra 40 minutos de presencia.",
    },
    {
      date: "2026-05-26",
      commission: "Asuntos Energéticos",
      status: "present",
      arrival: "10:00",
      departure: "10:50",
      durationMinutes: 50,
      sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026",
      note: "Presencia completa durante los 50 minutos registrados.",
    },
    {
      date: "2026-05-27",
      commission: "Deportes",
      status: "present",
      arrival: "09:30",
      departure: "10:30",
      durationMinutes: 60,
      sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026",
      note: "Presencia completa durante una hora.",
    },
  ],
};
