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
    { date: "2026-05-05", commission: "Comisión registrada en informe mensual del Senado", status: "present", arrival: "10:20", departure: "10:40", durationMinutes: 20, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026", note: "El informe oficial registra llegada, salida y 20 minutos de presencia." },
    { date: "2026-05-26", commission: "Asuntos Energéticos", status: "present", arrival: "10:00", departure: "10:50", durationMinutes: 50, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026", note: "Presencia completa durante los 50 minutos de la reunión registrada." },
  ],
  "gustavo-lara-salazar": [
    { date: "2026-05-06", commission: "Deportes", status: "present", arrival: "09:00", departure: "09:18", durationMinutes: 18, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026", note: "Presencia durante la totalidad de la reunión registrada." },
    { date: "2026-05-26", commission: "Asuntos Energéticos", status: "present", arrival: "10:05", departure: "10:50", durationMinutes: 45, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026", note: "Llegó cinco minutos después del inicio y permaneció hasta el cierre." },
    { date: "2026-05-27", commission: "Deportes", status: "present", arrival: "09:30", departure: "10:30", durationMinutes: 60, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026", note: "Presencia completa durante una hora." },
  ],
  "pedro-manuel-catrain-bonilla": [
    { date: "2026-05-19", commission: "Comisión Especial sobre integridad, control del financiamiento y prevención en la política · Exp. 01452", status: "present", arrival: "12:00", departure: "12:59", durationMinutes: 59, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026", note: "Presencia durante la totalidad de la reunión registrada." },
    { date: "2026-05-19", commission: "Reunión de comisión registrada en el informe mensual", status: "present", arrival: "10:40", departure: "11:26", durationMinutes: 46, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026", note: "El informe oficial registra 46 minutos de presencia." },
  ],
  "aracelis-villanueva-figueroa": [
    { date: "2026-05-12", commission: "Relaciones Exteriores y Cooperación Internacional", status: "present", arrival: "12:30", departure: "13:10", durationMinutes: 40, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026", note: "Presencia completa durante los 40 minutos de la reunión." },
    { date: "2026-05-19", commission: "Comisión Especial sobre integridad, control del financiamiento y prevención en la política · Exp. 01452", status: "present", arrival: "12:00", departure: "12:59", durationMinutes: 59, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026", note: "Presencia durante la totalidad de la reunión registrada." },
    { date: "2026-05-21", commission: "Asuntos de la Familia y Equidad de Género", status: "present", arrival: "10:00", departure: "11:45", durationMinutes: 105, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026", note: "Presencia completa durante 1 hora y 45 minutos." },
  ],
  "rafael-baron-duluc-rijo": [
    { date: "2026-05-05", commission: "Reunión de comisión registrada en informe mensual del Senado", status: "present", arrival: "10:00", departure: "10:40", durationMinutes: 40, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026", note: "El informe oficial registra 40 minutos de presencia." },
    { date: "2026-05-26", commission: "Asuntos Energéticos", status: "present", arrival: "10:00", departure: "10:50", durationMinutes: 50, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026", note: "Presencia completa durante los 50 minutos registrados." },
    { date: "2026-05-27", commission: "Deportes", status: "present", arrival: "09:30", departure: "10:30", durationMinutes: 60, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026", note: "Presencia completa durante una hora." },
  ],
  "odalis-rafael-rodriguez-rodriguez": [
    { date: "2025-06-04", commission: "Asuntos Agropecuarios y Agroindustrial", status: "present", arrival: "10:10", departure: "11:04", durationMinutes: 54, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/52831/asistencia-del-mes-de-junio-del-2025" },
    { date: "2025-06-04", commission: "Cultura", status: "present", arrival: "11:00", departure: "11:40", durationMinutes: 40, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/52831/asistencia-del-mes-de-junio-del-2025" },
    { date: "2025-07-16", commission: "Desarrollo Municipal y Organizaciones No Gubernamentales", status: "present", arrival: "13:00", departure: "15:30", durationMinutes: 150, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/53206/asistencia-del-mes-de-julio-del-2025" },
    { date: "2025-07-17", commission: "Comisión Bicameral · modificación Ley 42-01 General de Salud · Exp. 00674", status: "present", arrival: "10:08", departure: "10:47", durationMinutes: 39, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/53206/asistencia-del-mes-de-julio-del-2025" },
    { date: "2026-05-27", commission: "Deportes", status: "present", arrival: "10:00", departure: "10:30", durationMinutes: 30, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026" },
    { date: "2026-05-27", commission: "Desarrollo Municipal y Organizaciones No Gubernamentales", status: "present", arrival: "11:00", departure: "12:00", durationMinutes: 60, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026" },
  ],
  "maria-mercedes-ortiz-dilone": [
    { date: "2025-06-04", commission: "Cultura", status: "present", arrival: "11:00", departure: "11:40", durationMinutes: 40, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/52831/asistencia-del-mes-de-junio-del-2025" },
    { date: "2025-07-16", commission: "Desarrollo Municipal y Organizaciones No Gubernamentales", status: "present", arrival: "13:00", departure: "15:30", durationMinutes: 150, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/53206/asistencia-del-mes-de-julio-del-2025" },
    { date: "2026-05-27", commission: "Deportes", status: "present", arrival: "10:00", departure: "10:30", durationMinutes: 30, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026" },
    { date: "2026-05-27", commission: "Desarrollo Municipal y Organizaciones No Gubernamentales", status: "present", arrival: "11:00", departure: "12:00", durationMinutes: 60, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026" },
  ],
  "daniel-enrique-rivera-reyes": [
    { date: "2025-07-17", commission: "Comisión Bicameral · modificación Ley 42-01 General de Salud · Exp. 00674", status: "present", arrival: "10:17", departure: "10:47", durationMinutes: 30, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/53206/asistencia-del-mes-de-julio-del-2025" },
    { date: "2026-05-27", commission: "Desarrollo Municipal y Organizaciones No Gubernamentales", status: "present", arrival: "11:00", departure: "12:00", durationMinutes: 60, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026" },
  ],
  "andres-guillermo-lama-perez": [
    { date: "2025-07-16", commission: "Desarrollo Municipal y Organizaciones No Gubernamentales", status: "present", arrival: "13:00", departure: "15:30", durationMinutes: 150, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/53206/asistencia-del-mes-de-julio-del-2025" },
    { date: "2025-07-17", commission: "Comisión Bicameral · modificación Ley 42-01 General de Salud · Exp. 00674", status: "present", arrival: "10:46", departure: "10:47", durationMinutes: 1, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/53206/asistencia-del-mes-de-julio-del-2025", note: "El informe oficial registra un minuto de permanencia en esta reunión concreta." },
    { date: "2026-05-27", commission: "Desarrollo Municipal y Organizaciones No Gubernamentales", status: "present", arrival: "11:00", departure: "12:00", durationMinutes: 60, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026" },
  ],
  "milciades-aneudy-ortiz-sajiun": [
    { date: "2025-06-04", commission: "Asuntos Agropecuarios y Agroindustrial", status: "present", arrival: "10:41", departure: "11:04", durationMinutes: 23, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/52831/asistencia-del-mes-de-junio-del-2025" },
    { date: "2025-07-16", commission: "Desarrollo Municipal y Organizaciones No Gubernamentales", status: "present", arrival: "13:00", departure: "15:30", durationMinutes: 150, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/53206/asistencia-del-mes-de-julio-del-2025" },
    { date: "2026-05-27", commission: "Desarrollo Municipal y Organizaciones No Gubernamentales", status: "present", arrival: "11:00", departure: "12:00", durationMinutes: 60, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/60403/asistencia-del-mes-de-mayo-de-2026" },
  ],
  "manuel-maria-rodriguez-ortega": [
    { date: "2025-06-04", commission: "Asuntos Agropecuarios y Agroindustrial", status: "present", arrival: "10:20", departure: "11:04", durationMinutes: 44, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/52831/asistencia-del-mes-de-junio-del-2025" },
  ],
  "bernardo-aleman-rodriguez": [
    { date: "2025-06-04", commission: "Asuntos Agropecuarios y Agroindustrial", status: "present", arrival: "10:20", departure: "11:04", durationMinutes: 44, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/52831/asistencia-del-mes-de-junio-del-2025" },
  ],
  "franklin-martin-romero-morillo": [
    { date: "2025-06-04", commission: "Asuntos Agropecuarios y Agroindustrial", status: "present", arrival: "10:25", departure: "11:04", durationMinutes: 39, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/52831/asistencia-del-mes-de-junio-del-2025" },
    { date: "2025-06-04", commission: "Cultura", status: "present", arrival: "11:00", departure: "11:40", durationMinutes: 40, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/52831/asistencia-del-mes-de-junio-del-2025" },
  ],
  "carlos-manuel-gomez-urena": [
    { date: "2025-06-04", commission: "Cultura", status: "present", arrival: "11:00", departure: "11:40", durationMinutes: 40, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/52831/asistencia-del-mes-de-junio-del-2025" },
  ],
  "secundino-velazquez-pimentel": [
    { date: "2025-07-16", commission: "Desarrollo Municipal y Organizaciones No Gubernamentales", status: "present", arrival: "13:00", departure: "15:30", durationMinutes: 150, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/53206/asistencia-del-mes-de-julio-del-2025" },
  ],
  "cristobal-venerado-castillo-liriano": [
    { date: "2025-07-16", commission: "Desarrollo Municipal y Organizaciones No Gubernamentales", status: "present", arrival: "13:00", departure: "15:30", durationMinutes: 150, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/53206/asistencia-del-mes-de-julio-del-2025" },
  ],
  "lia-ynocencia-diaz-santana": [
    { date: "2025-07-17", commission: "Comisión Bicameral · modificación Ley 42-01 General de Salud · Exp. 00674", status: "present", arrival: "10:10", departure: "10:47", durationMinutes: 37, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/53206/asistencia-del-mes-de-julio-del-2025" },
  ],
  "eduard-alexis-espiritusanto-castillo": [
    { date: "2025-07-17", commission: "Comisión Bicameral · modificación Ley 42-01 General de Salud · Exp. 00674", status: "present", arrival: "10:23", departure: "10:47", durationMinutes: 24, sourceUrl: "https://www.senadord.gob.do/Descargas/1383/asistencia-comisiones/53206/asistencia-del-mes-de-julio-del-2025" },
  ],
};