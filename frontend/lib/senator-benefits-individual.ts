export type IndividualSenateBenefit = {
  label: string;
  monthlyAmount?: number;
  status: "verified" | "does_not_receive" | "reported";
  kind: "personal_income" | "social_fund";
  sourceUrl: string;
  note?: string;
};

/**
 * Beneficios/asignaciones individualizados solo cuando existe una fuente que
 * permite atribuir el monto al senador concreto. El barrilito es un fondo
 * institucional de asistencia social y NO salario personal.
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
    { label: "Fondo de asistencia social (barrilito)", status: "does_not_receive", kind: "social_fund", sourceUrl: "https://epaper.diariolibre.com/epaper/xml_epaper/diariolibremetro/07_01_2025/pla_502_Planillo/pdf_pags/502.pdf?t=1296384000", note: "La fuente documenta que renunció al fondo y mantiene esa posición en el período reseñado." },
  ],
  "ramon-rogelio-genao-duran": [
    { label: "Fondo de asistencia social (barrilito)", monthlyAmount: 994000, status: "reported", kind: "social_fund", sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/01/07/el-barrilito-va-en-ascenso-en-el-periodo-2024-2028/2957404", note: "Asignación reportada para La Vega; fondo provincial/institucional." },
  ],
  "ginnette-altagracia-bournigal": [
    { label: "Fondo de asistencia social (barrilito)", monthlyAmount: 869000, status: "reported", kind: "social_fund", sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/01/07/el-barrilito-va-en-ascenso-en-el-periodo-2024-2028/2957404", note: "Asignación reportada para Puerto Plata; fondo provincial/institucional." },
  ],
  "aracelis-villanueva-figueroa": [
    { label: "Fondo de asistencia social (barrilito)", monthlyAmount: 859000, status: "reported", kind: "social_fund", sourceUrl: "https://www.diariolibre.com/politica/congreso-nacional/2025/01/07/el-barrilito-va-en-ascenso-en-el-periodo-2024-2028/2957404", note: "Asignación reportada para San Pedro de Macorís; fondo provincial/institucional." },
  ],
};