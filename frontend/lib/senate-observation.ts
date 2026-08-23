export type SenateCompensationItem = {
  label: string;
  amount?: number;
  unit: "monthly" | "per_session" | "variable";
  status: "verified" | "reported" | "requires_current_verification";
  description: string;
  sourceUrl: string;
};

export const senateObservationSources = {
  attendance: "https://www.senadord.gob.do/elaboracion-de-actas/asistencia-a-sesiones/",
  initiatives: "https://www.senadord.gob.do/secretaria-general-legislativa/iniciativas-legislativas/",
  approvedInitiatives: "https://www.senadord.gob.do/secretaria-general-legislativa/iniciativas-aprobadas/",
  openData: "https://transparencia.senadord.gob.do/datos-abiertos/",
};

// Compensation is deliberately split by provenance/status. A senator's fixed
// salary is corroborated by an official 2024 sworn asset declaration. Other
// recurring benefits have been publicly reported but should not be presented
// as current 2026 entitlements until the OED has attached the corresponding
// current Senate transparency record.
export const senateCompensation: SenateCompensationItem[] = [
  {
    label: "Salario fijo",
    amount: 320000,
    unit: "monthly",
    status: "verified",
    description: "Remuneración mensual fija del cargo de senador/a.",
    sourceUrl:
      "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43668/manuel-maria-rodriguez-ortega.pdf",
  },
  {
    label: "Gastos de representación",
    amount: 50000,
    unit: "monthly",
    status: "requires_current_verification",
    description:
      "Compensación de representación reportada públicamente. El OED la muestra separada del salario y pendiente de corroboración contra el registro oficial vigente.",
    sourceUrl:
      "https://www.diariolibre.com/actualidad/politica/senado-de-la-republica-corre-con-los-gastos-de-los-empleados-de-las-oficinas-senatoriales-NF22277659",
  },
  {
    label: "Viáticos",
    amount: 25000,
    unit: "monthly",
    status: "requires_current_verification",
    description:
      "Monto reportado para viáticos; requiere actualización documental individual/institucional para 2026.",
    sourceUrl:
      "https://www.diariolibre.com/actualidad/politica/senado-de-la-republica-corre-con-los-gastos-de-los-empleados-de-las-oficinas-senatoriales-NF22277659",
  },
  {
    label: "Dieta por sesión",
    amount: 3500,
    unit: "per_session",
    status: "reported",
    description:
      "Remuneración adicional asociada a la asistencia a sesiones, reportada históricamente. La asistencia oficial se documenta por sesión.",
    sourceUrl:
      "https://www.diariolibre.com/actualidad/politica/senado-de-la-republica-corre-con-los-gastos-de-los-empleados-de-las-oficinas-senatoriales-NF22277659",
  },
  {
    label: "Fondo de gestión social / oficina senatorial",
    unit: "variable",
    status: "requires_current_verification",
    description:
      "No es salario personal. Históricamente ha existido una asignación variable asociada a gestión social/oficina senatorial. Debe mostrarse separada de la remuneración personal y con el monto vigente por provincia cuando se verifique.",
    sourceUrl:
      "https://listindiario.com/la-republica/2020/11/12/643662/el-barrilito-detalles-ocultos-de-un-fondo-para-asistencia-social/amp.html",
  },
];

export type SenatorInitiative = {
  number?: string;
  title: string;
  role?: string;
  status: "introduced" | "committee" | "approved_senate" | "approved_congress" | "promulgated" | "rejected" | "expired" | "withdrawn" | "unknown";
  introducedAt?: string;
  documentUrl?: string;
  sourceUrl: string;
};

// Per-senator initiative and attendance observations will be progressively
// populated from the official Senate systems. Keeping the schema here means
// every public profile can expose the sections immediately without inventing
// counts while documentary extraction is still incomplete.
export const senatorInitiatives: Record<string, SenatorInitiative[]> = {};

export type SenatorAttendance = {
  period: string;
  plenarySessions?: number;
  attended?: number;
  excused?: number;
  unjustifiedAbsences?: number;
  sourceUrl: string;
};

export const senatorAttendance: Record<string, SenatorAttendance[]> = {};
