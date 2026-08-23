export type SenateCompensationItem = {
  label: string;
  amount?: number;
  unit: "monthly" | "per_session" | "variable" | "per_two_years" | "entitlement";
  status: "verified" | "reported" | "requires_current_verification";
  kind: "personal_income" | "institutional_support" | "social_fund" | "tax_benefit" | "social_security";
  description: string;
  sourceUrl: string;
  legalBasis?: string;
};

export const senateObservationSources = {
  attendance: "https://www.senadord.gob.do/elaboracion-de-actas/asistencia-a-sesiones/",
  initiatives: "https://www.senadord.gob.do/secretaria-general-legislativa/iniciativas-legislativas/",
  approvedInitiatives: "https://www.senadord.gob.do/secretaria-general-legislativa/iniciativas-aprobadas/",
  openData: "https://transparencia.senadord.gob.do/datos-abiertos/",
  transparency: "https://transparencia.senadord.gob.do/",
  senateRules: "https://transparencia.senadord.gob.do/download/725/resoluciones/43294/reglamento-del-senado-rep-dom.pdf",
  vehicleExemption:
    "https://vucerd.gob.do/media/2307/exoneraci%C3%B3n-de-impuestos-de-importaci%C3%B3n-a-senadores-y-diputados-de-la-rep%C3%BAblica-dominicana-ley-57-96.pdf",
};

// IMPORTANT: benefits are not uniform across all senators. The sworn asset
// declarations published by the Senate/Cámara de Cuentas show different
// amounts for fuel, representation, diets and lodging. The OED therefore
// exposes these items as variable until each senator's current declaration or
// Senate payment record is attached to the individual profile.
export const senateCompensation: SenateCompensationItem[] = [
  {
    label: "Salario fijo",
    amount: 320000,
    unit: "monthly",
    status: "verified",
    kind: "personal_income",
    description:
      "Remuneración mensual bruta del cargo. Declaraciones juradas de senadores del período 2024–2028 registran RD$320,000 mensuales.",
    sourceUrl:
      "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/41290/alexis-victoria-yeb.pdf",
  },
  {
    label: "Gastos de representación",
    unit: "variable",
    status: "verified",
    kind: "personal_income",
    description:
      "Ingreso/compensación mensual que aparece en declaraciones juradas recientes, pero su monto no es idéntico para todos. Se han documentado valores de RD$24,000 y RD$48,000 mensuales. El OED lo fijará por senador cuando conecte su declaración individual.",
    sourceUrl:
      "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43672/milciades-aneudy-ortiz-sajiun.pdf",
  },
  {
    label: "Combustible",
    unit: "variable",
    status: "verified",
    kind: "personal_income",
    description:
      "Asignación mensual documentada en declaraciones juradas del período vigente. Los montos observados no son uniformes: existen registros de RD$16,000 y RD$32,000 mensuales, por lo que se mostrará el valor individual de cada senador.",
    sourceUrl:
      "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/41290/alexis-victoria-yeb.pdf",
  },
  {
    label: "Dietas",
    unit: "variable",
    status: "verified",
    kind: "personal_income",
    description:
      "Compensación adicional registrada en declaraciones juradas. Un registro oficial reciente reporta RD$24,600 mensuales; el monto individual debe verificarse antes de atribuirlo a cada senador.",
    sourceUrl:
      "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/41290/alexis-victoria-yeb.pdf",
  },
  {
    label: "Hospedaje",
    unit: "variable",
    status: "verified",
    kind: "personal_income",
    description:
      "Beneficio/ingreso que aparece en algunas declaraciones juradas. Pedro Catrain, por ejemplo, declara RD$48,000 mensuales. No debe asumirse que todos los senadores lo reciben.",
    sourceUrl:
      "https://www.transparencia.senadord.gob.do/wp-content/uploads/wpfd/preview_files/PEDRO-MANUEL-CATRAIN-BONILLA%28443ecbd48bc81e881b05d044e4376b6f%29.pdf",
  },
  {
    label: "Fondo de asistencia social (\"barrilito\")",
    unit: "variable",
    status: "verified",
    kind: "social_fund",
    description:
      "Fondo institucional para gestión/asistencia social en la provincia; no es salario personal. Sigue activo en 2026 y su asignación varía por demarcación. El OED mostrará el monto mensual de cada provincia y si el senador lo recibe o ha renunciado a él.",
    sourceUrl:
      "https://www.diariolibre.com/politica/congreso-nacional/2026/03/26/el-barrilito-no-desaparecera-pese-a-crisis-internacional/3481793",
  },
  {
    label: "Exoneración de vehículo",
    unit: "per_two_years",
    status: "verified",
    kind: "tax_benefit",
    description:
      "La Ley 57-96 permite a cada legislador importar libre de impuestos un vehículo de motor cada dos años. Es un beneficio tributario, no un pago mensual en efectivo.",
    sourceUrl: senateObservationSources.vehicleExemption,
    legalBasis: "Ley 57-96 sobre exoneraciones a miembros del Poder Legislativo",
  },
  {
    label: "Seguridad social: salud y pensiones",
    unit: "entitlement",
    status: "verified",
    kind: "social_security",
    description:
      "El Reglamento del Senado reconoce a los senadores el derecho a seguridad social en salud y pensiones conforme al Sistema Dominicano de Seguridad Social y a disposiciones internas aplicables.",
    sourceUrl: senateObservationSources.senateRules,
    legalBasis: "Reglamento del Senado, artículo 51",
  },
  {
    label: "Personal y apoyo logístico",
    unit: "entitlement",
    status: "verified",
    kind: "institutional_support",
    description:
      "El Reglamento del Senado reconoce el derecho a disponer de personal y apoyo logístico tanto en la sede del Congreso como en oficinas provinciales. Esto es soporte institucional, no remuneración personal.",
    sourceUrl: senateObservationSources.senateRules,
    legalBasis: "Reglamento del Senado, artículo 60, numeral 16",
  },
];

export const senateBenefitResearchNotes = [
  {
    claim: "Pago general de colegiatura de hijos de senadores",
    status: "not_verified" as const,
    note:
      "La revisión legal y documental realizada hasta ahora no ha localizado una norma general que garantice al senador el pago de la colegiatura de sus hijos. No se publicará como beneficio sin una fuente normativa o financiera específica.",
  },
  {
    claim: "Seguro médico internacional/VIP",
    status: "historically_reported" as const,
    note:
      "Ha sido reportado en prensa en períodos anteriores, pero el Reglamento vigente solo garantiza seguridad social en salud y pensiones. El OED requiere póliza, contrato o ejecución presupuestaria vigente antes de marcarlo como beneficio actual.",
  },
  {
    claim: "Chofer, seguridad, celulares, oficina y otros apoyos",
    status: "partially_verified" as const,
    note:
      "El Reglamento sí reconoce personal y apoyo logístico. Los componentes concretos y costos por senador deben documentarse con nómina, contratos y ejecución presupuestaria antes de cuantificarse individualmente.",
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
