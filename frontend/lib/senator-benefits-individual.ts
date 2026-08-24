import { senators } from "@/lib/legislators";

export type IndividualSenateBenefit = {
  label: string;
  monthlyAmount?: number;
  status: "verified" | "does_not_receive" | "reported";
  kind: "personal_income" | "social_fund";
  sourceUrl: string;
  note?: string;
};

const panoramaBenefitsSource =
  "https://panorama.com.do/ante-la-falta-de-auditoria-privilegios-de-legisladores-se-mantienen-y-oscurecen-la-labor-legislativa/";

/**
 * Beneficios/asignaciones individualizados solo cuando existe una fuente que
 * permite atribuir el monto o el estado de recepción al senador concreto.
 * El barrilito es un fondo institucional de asistencia social y NO salario personal.
 */
export const individualSenateBenefits: Record<string, IndividualSenateBenefit[]> = {
  "alexis-victoria-yeb": [
    { label: "Gastos de representación", monthlyAmount: 48000, status: "verified", kind: "personal_income", sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/41290/alexis-victoria-yeb.pdf" },
    { label: "Combustible", monthlyAmount: 32000, status: "verified", kind: "personal_income", sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/41290/alexis-victoria-yeb.pdf" },
    { label: "Dietas", monthlyAmount: 24600, status: "verified", kind: "personal_income", sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/41290/alexis-victoria-yeb.pdf" },
  ],
  "milciades-aneudy-ortiz-sajiun": [
    { label: "Gastos de representación", monthlyAmount: 48000, status: "verified", kind: "personal_income", sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43672/milciades-aneudy-ortiz-sajiun.pdf" },
    { label: "Combustible", monthlyAmount: 32000, status: "verified", kind: "personal_income", sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43672/milciades-aneudy-ortiz-sajiun.pdf" },
  ],
  "pedro-manuel-catrain-bonilla": [
    { label: "Gastos de representación", monthlyAmount: 24000, status: "verified", kind: "personal_income", sourceUrl: "https://www.transparencia.senadord.gob.do/wp-content/uploads/wpfd/preview_files/PEDRO-MANUEL-CATRAIN-BONILLA%28443ecbd48bc81e881b05d044e4376b6f%29.pdf" },
    { label: "Combustible", monthlyAmount: 32000, status: "verified", kind: "personal_income", sourceUrl: "https://www.transparencia.senadord.gob.do/wp-content/uploads/wpfd/preview_files/PEDRO-MANUEL-CATRAIN-BONILLA%28443ecbd48bc81e881b05d044e4376b6f%29.pdf" },
    { label: "Hospedaje", monthlyAmount: 48000, status: "verified", kind: "personal_income", sourceUrl: "https://www.transparencia.senadord.gob.do/wp-content/uploads/wpfd/preview_files/PEDRO-MANUEL-CATRAIN-BONILLA%28443ecbd48bc81e881b05d044e4376b6f%29.pdf" },
  ],
  "gustavo-lara-salazar": [
    { label: "Combustible", monthlyAmount: 16000, status: "verified", kind: "personal_income", sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43663/gustavo-lara-salazar.pdf" },
    { label: "Gastos de representación", monthlyAmount: 48000, status: "verified", kind: "personal_income", sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43663/gustavo-lara-salazar.pdf" },
    { label: "Hospedaje", monthlyAmount: 24000, status: "verified", kind: "personal_income", sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43663/gustavo-lara-salazar.pdf" },
    { label: "Fondo de asistencia social (barrilito)", monthlyAmount: 1059000, status: "reported", kind: "social_fund", sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/08/16/como-concluyo-la-pasada-legislatura-senatorial/3214742", note: "Fondo provincial/institucional; no es salario personal." },
  ],
  "moises-ayala-perez": [
    { label: "Gastos de representación", monthlyAmount: 48000, status: "verified", kind: "personal_income", sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43667/moises-ayala-perez.pdf" },
    { label: "Otros ingresos declarados", monthlyAmount: 24000, status: "verified", kind: "personal_income", sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43667/moises-ayala-perez.pdf", note: "El formulario los denomina otros ingresos; el OED no los reclasifica automáticamente como dietas." },
  ],
  "franklin-martin-romero-morillo": [
    { label: "Gastos de representación", monthlyAmount: 24000, status: "verified", kind: "personal_income", sourceUrl: "https://transparencia.senadord.gob.do/wp-content/uploads/wpfd/preview_files/FRANKLIN-MARTIN-ROMERO-MORILLO%28af5f1871fc32857b6d868452b4addac7%29.pdf" },
    { label: "Combustible", monthlyAmount: 32000, status: "verified", kind: "personal_income", sourceUrl: "https://transparencia.senadord.gob.do/wp-content/uploads/wpfd/preview_files/FRANKLIN-MARTIN-ROMERO-MORILLO%28af5f1871fc32857b6d868452b4addac7%29.pdf" },
    { label: "Hospedaje", monthlyAmount: 48000, status: "verified", kind: "personal_income", sourceUrl: "https://transparencia.senadord.gob.do/wp-content/uploads/wpfd/preview_files/FRANKLIN-MARTIN-ROMERO-MORILLO%28af5f1871fc32857b6d868452b4addac7%29.pdf" },
  ],
  "omar-leonel-fernandez-dominguez": [
    { label: "Fondo de asistencia social (barrilito)", monthlyAmount: 1059000, status: "reported", kind: "social_fund", sourceUrl: "https://epaper.diariolibre.com/epaper/xml_epaper/diariolibremetro/07_01_2025/pla_502_Planillo/pdf_pags/502.pdf?t=1296384000", note: "Fondo provincial/institucional; no es salario personal." },
  ],
  "daniel-enrique-rivera-reyes": [
    { label: "Fondo de asistencia social (barrilito)", monthlyAmount: 1059000, status: "reported", kind: "social_fund", sourceUrl: "https://epaper.diariolibre.com/epaper/xml_epaper/diariolibremetro/07_01_2025/pla_502_Planillo/pdf_pags/502.pdf?t=1296384000", note: "Fondo provincial/institucional; no es salario personal." },
  ],
  "antonio-manuel-taveras-guzman": [
    { label: "Fondo de asistencia social (barrilito)", status: "does_not_receive", kind: "social_fund", sourceUrl: panoramaBenefitsSource, note: "La investigación de 2025 identifica a Antonio Taveras como el único senador del período 2024-2028 que no recibe este fondo." },
    { label: "Ingresos legislativos mensuales declarados (total)", monthlyAmount: 347000, status: "reported", kind: "personal_income", sourceUrl: panoramaBenefitsSource, note: "Total mensual derivado de la declaración jurada de agosto de 2024. Incluye salario y otras remuneraciones; la fuente no publica un desglose completo de cada partida." },
  ],
  "ramon-rogelio-genao-duran": [
    { label: "Fondo de asistencia social (barrilito)", monthlyAmount: 994000, status: "reported", kind: "social_fund", sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/01/07/el-barrilito-va-en-ascenso-en-el-periodo-2024-2028/2957404", note: "Asignación reportada para La Vega; fondo provincial/institucional." },
    { label: "Representación + combustible + hospedaje (combinado)", monthlyAmount: 104000, status: "reported", kind: "personal_income", sourceUrl: panoramaBenefitsSource, note: "La fuente atribuye RD$104,000 mensuales adicionales al salario de RD$320,000, pero no desglosa cuánto corresponde a cada uno de los tres conceptos." },
  ],
  "ginnette-altagracia-bournigal": [
    { label: "Fondo de asistencia social (barrilito)", monthlyAmount: 869000, status: "reported", kind: "social_fund", sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/01/07/el-barrilito-va-en-ascenso-en-el-periodo-2024-2028/2957404", note: "Asignación reportada para Puerto Plata; fondo provincial/institucional." },
  ],
  "aracelis-villanueva-figueroa": [
    { label: "Fondo de asistencia social (barrilito)", monthlyAmount: 859000, status: "reported", kind: "social_fund", sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/01/07/el-barrilito-va-en-ascenso-en-el-periodo-2024-2028/2957404", note: "Asignación reportada para San Pedro de Macorís; fondo provincial/institucional." },
  ],
  "felix-ramon-bautista-rosario": [
    { label: "Ingresos legislativos mensuales declarados (total)", monthlyAmount: 487142, status: "reported", kind: "personal_income", sourceUrl: panoramaBenefitsSource, note: "Monto mensual equivalente publicado a partir de su declaración jurada. Incluye salario y otras remuneraciones; el OED no infiere el desglose no publicado." },
  ],
  "ricardo-de-los-santos-polanco": [
    { label: "Compensación por bufete directivo", monthlyAmount: 67000, status: "reported", kind: "personal_income", sourceUrl: panoramaBenefitsSource, note: "Equivalente mensual de RD$800,000 anuales declarados por integrar el bufete directivo." },
    { label: "Combustible", monthlyAmount: 25333.33, status: "reported", kind: "personal_income", sourceUrl: panoramaBenefitsSource, note: "Equivalente mensual de RD$304,000 anuales declarados." },
    { label: "Dieta", monthlyAmount: 20758.33, status: "reported", kind: "personal_income", sourceUrl: panoramaBenefitsSource, note: "Equivalente mensual de RD$249,100 anuales declarados." },
    { label: "Gastos de representación", monthlyAmount: 42500, status: "reported", kind: "personal_income", sourceUrl: panoramaBenefitsSource, note: "Equivalente mensual de RD$510,000 anuales declarados." },
    { label: "Hospedaje", monthlyAmount: 40000, status: "reported", kind: "personal_income", sourceUrl: panoramaBenefitsSource, note: "Equivalente mensual de RD$480,000 anuales declarados." },
  ],
};

// Cobertura de estado del barrilito 32/32 para el período 2024-2028.
// Panorama reporta que solo Antonio Taveras no recibe el fondo. Para los demás
// se registra recepción sin inventar monto cuando la asignación provincial exacta
// todavía no ha sido reconciliada en el OED.
for (const senator of senators) {
  const benefits = (individualSenateBenefits[senator.id] ??= []);
  const hasBarrilito = benefits.some((item) => item.label.includes("barrilito"));
  if (!hasBarrilito) {
    benefits.push({
      label: "Fondo de asistencia social (barrilito)",
      status: "reported",
      kind: "social_fund",
      sourceUrl: panoramaBenefitsSource,
      note: "La investigación de 2025 reporta que el senador recibe el fondo en el período 2024-2028. El monto provincial exacto queda pendiente de reconciliación documental; no es salario personal.",
    });
  }
}
