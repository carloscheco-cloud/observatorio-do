export type SenatorPatrimonySnapshot = {
  senatorId: string;
  declarationPeriod: string;
  declarationUrl: string;
  declarationLinkType: "direct_pdf" | "official_portal" | "official_record";
  reportedAssets?: number;
  reportedLiabilities?: number;
  reportedNetWorth?: number;
  sourceUrl: string;
  sourceLabel: string;
  priorDeclarationId?: string;
  note?: string;
};

const senateDeclarationPortal =
  "https://transparencia.senadord.gob.do/declaraciones-juradas-de-patrimonio/";

const dlPatrimony = "https://flo.uri.sh/visualisation/19660033/embed";

/**
 * Primera ola patrimonial: 16 primeros senadores del roster 2024-2028.
 * Los valores se publican como activos/pasivos/patrimonio neto solo cuando la
 * fuente consultada permite identificarlos con esa semántica. Cuando el
 * documento individual todavía no se ha resuelto, se enlaza el portal oficial
 * y no se inventa un PDF.
 */
export const senatorPatrimonyFirst16: Record<string, SenatorPatrimonySnapshot> = {
  "lia-ynocencia-diaz-santana": {
    senatorId: "lia-ynocencia-diaz-santana",
    declarationPeriod: "2024",
    declarationUrl: senateDeclarationPortal,
    declarationLinkType: "official_portal",
    reportedAssets: 46480492.51,
    reportedLiabilities: 6952503.52,
    reportedNetWorth: 39527988.99,
    sourceUrl: "https://diariopuertoplata.com.do/fortuna-de-carlos-gomez-ronda-los-9-9-billones-y-es-mayor-a-la-de-todos-los-senadores-juntos/",
    sourceLabel: "Datos de declaración jurada reproducidos a partir de Cámara de Cuentas",
    note: "El OED mantiene el portal oficial hasta resolver el PDF individual vigente. La nómina del Senado confirma salario bruto mensual de RD$320,000.",
  },
  "andres-guillermo-lama-perez": {
    senatorId: "andres-guillermo-lama-perez",
    declarationPeriod: "2024",
    declarationUrl: senateDeclarationPortal,
    declarationLinkType: "official_portal",
    reportedAssets: 61045383.98,
    reportedLiabilities: 1,
    reportedNetWorth: 61045382.98,
    sourceUrl: dlPatrimony,
    sourceLabel: "Visualización de declaraciones juradas basada en Cámara de Cuentas · Diario Libre",
    note: "La visualización de octubre de 2024 publicó RD$61,045,383.98 como total. Una revisión posterior reportó pasivos de RD$1.00.",
  },
  "moises-ayala-perez": {
    senatorId: "moises-ayala-perez",
    declarationPeriod: "2024-08-16",
    declarationUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43667/moises-ayala-perez.pdf",
    declarationLinkType: "direct_pdf",
    reportedAssets: 70077249.89,
    reportedLiabilities: 16333427.87,
    reportedNetWorth: 53743822.02,
    sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43667/moises-ayala-perez.pdf",
    sourceLabel: "Declaración jurada oficial DJP-42469",
    priorDeclarationId: "22964",
    note: "Cambio de cargo al Senado. El formulario identifica una declaración anterior rectificativa ID 22964.",
  },
  "manuel-maria-rodriguez-ortega": {
    senatorId: "manuel-maria-rodriguez-ortega",
    declarationPeriod: "2024-08-16",
    declarationUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43668/manuel-maria-rodriguez-ortega.pdf",
    declarationLinkType: "direct_pdf",
    reportedAssets: 51716557.8,
    reportedLiabilities: 12562099.21,
    reportedNetWorth: 39154458.59,
    sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43668/manuel-maria-rodriguez-ortega.pdf",
    sourceLabel: "Declaración jurada oficial DJP-42287",
    priorDeclarationId: "21678",
    note: "Cambio de cargo al Senado. El formulario identifica una declaración anterior rectificativa ID 21678.",
  },
  "omar-leonel-fernandez-dominguez": {
    senatorId: "omar-leonel-fernandez-dominguez",
    declarationPeriod: "2024",
    declarationUrl: senateDeclarationPortal,
    declarationLinkType: "official_portal",
    reportedAssets: 13846391.58,
    reportedLiabilities: 2600000,
    reportedNetWorth: 11246391.58,
    sourceUrl: "https://www.diariolibre.com/politica/gobierno/2024/10/09/entre-politica-y-negocios-las-fortunas-de-los-senadores-dominicanos/2875604",
    sourceLabel: "Diario Libre · análisis de declaraciones publicadas por Cámara de Cuentas",
    note: "La fuente periodística reporta aproximadamente RD$2.6 millones en pasivos y patrimonio neto cercano a RD$11.1 millones; se conserva el portal oficial hasta resolver el PDF exacto.",
  },
  "franklin-martin-romero-morillo": {
    senatorId: "franklin-martin-romero-morillo",
    declarationPeriod: "2024",
    declarationUrl: "https://transparencia.senadord.gob.do/wp-content/uploads/wpfd/preview_files/FRANKLIN-MARTIN-ROMERO-MORILLO%28af5f1871fc32857b6d868452b4addac7%29.pdf",
    declarationLinkType: "direct_pdf",
    reportedAssets: 471849192.81,
    sourceUrl: "https://transparencia.senadord.gob.do/wp-content/uploads/wpfd/preview_files/FRANKLIN-MARTIN-ROMERO-MORILLO%28af5f1871fc32857b6d868452b4addac7%29.pdf",
    sourceLabel: "Declaración jurada oficial DJP-019053",
    note: "El PDF oficial permite auditar inmuebles, empresas, ingresos y demás componentes. El total patrimonial consolidado se mantiene separado hasta terminar el recálculo completo por monedas.",
  },
  "santiago-jose-zorrilla": {
    senatorId: "santiago-jose-zorrilla",
    declarationPeriod: "2024",
    declarationUrl: senateDeclarationPortal,
    declarationLinkType: "official_portal",
    reportedAssets: 181433093.6,
    sourceUrl: dlPatrimony,
    sourceLabel: "Visualización de declaraciones juradas basada en Cámara de Cuentas · Diario Libre",
    note: "El senador explicó públicamente que el crecimiento real de su patrimonio entre 2020 y 2024 fue de aproximadamente RD$26 millones y cuestionó sumas automáticas del sistema de la Cámara de Cuentas. El OED no interpretará variaciones como irregularidad.",
  },
  "jonhson-encarnacion-diaz": {
    senatorId: "jonhson-encarnacion-diaz",
    declarationPeriod: "2024-08-16",
    declarationUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43670/jonhson-encarnacion-diaz.pdf",
    declarationLinkType: "direct_pdf",
    reportedAssets: 86320279.23,
    sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43670/jonhson-encarnacion-diaz.pdf",
    sourceLabel: "Declaración jurada oficial DJP-42652",
    note: "Declaración de inicio en el cargo. El total de activos publicado por la visualización de Cámara de Cuentas/Diario Libre es RD$86,320,279.23.",
  },
  "carlos-manuel-gomez-urena": {
    senatorId: "carlos-manuel-gomez-urena",
    declarationPeriod: "oct. 2024",
    declarationUrl: senateDeclarationPortal,
    declarationLinkType: "official_portal",
    reportedAssets: 9942000000,
    reportedNetWorth: 9940000000,
    sourceUrl: "https://www.diariolibre.com/amp/politica/general/2025/03/10/carlos-gomez-provincia-espaillat-es-el-senador-mas-adinerado-segun-cc/3028127",
    sourceLabel: "Diario Libre · datos de declaración ante Cámara de Cuentas",
    note: "La fuente reporta alrededor de RD$9,942 millones en activos y RD$9,940 millones de patrimonio neto, además de inversiones y activos en pesos y dólares. Las monedas no se mezclan en el OED sin política explícita de conversión.",
  },
  "cristobal-venerado-castillo-liriano": {
    senatorId: "cristobal-venerado-castillo-liriano",
    declarationPeriod: "2024",
    declarationUrl: senateDeclarationPortal,
    declarationLinkType: "official_portal",
    reportedAssets: 752427719.84,
    reportedNetWorth: 752427719.84,
    sourceUrl: dlPatrimony,
    sourceLabel: "Visualización de declaraciones juradas basada en Cámara de Cuentas · Diario Libre",
    note: "El consolidado publicado lo sitúa entre los mayores patrimonios del Senado. El OED mantiene el valor como cifra declarada/publicada, no como valoración independiente.",
  },
  "maria-mercedes-ortiz-dilone": {
    senatorId: "maria-mercedes-ortiz-dilone",
    declarationPeriod: "2024",
    declarationUrl: senateDeclarationPortal,
    declarationLinkType: "official_portal",
    reportedAssets: 8968923.26,
    reportedLiabilities: 4200000,
    reportedNetWorth: 4768923.26,
    sourceUrl: "https://www.diariolibre.com/politica/gobierno/2024/10/09/entre-politica-y-negocios-las-fortunas-de-los-senadores-dominicanos/2875604",
    sourceLabel: "Diario Libre · análisis de declaraciones publicadas por Cámara de Cuentas",
    note: "La fuente reporta pasivos cercanos a RD$4.2 millones. El OED mostrará el PDF individual cuando quede resuelto de forma exacta.",
  },
  "dagoberto-rodriguez-adames": {
    senatorId: "dagoberto-rodriguez-adames",
    declarationPeriod: "2024",
    declarationUrl: senateDeclarationPortal,
    declarationLinkType: "official_portal",
    reportedAssets: 60513716.41,
    reportedLiabilities: 27845595.94,
    reportedNetWorth: 32668120.47,
    sourceUrl: "https://diariopuertoplata.com.do/fortuna-de-carlos-gomez-ronda-los-9-9-billones-y-es-mayor-a-la-de-todos-los-senadores-juntos/",
    sourceLabel: "Datos de declaración jurada reproducidos a partir de Cámara de Cuentas",
    note: "El OED conserva estas cifras como snapshot publicado y mantiene pendiente la resolución del PDF oficial individual.",
  },
  "rafael-baron-duluc-rijo": {
    senatorId: "rafael-baron-duluc-rijo",
    declarationPeriod: "2024-08-16",
    declarationUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43659/rafael-baron-duluc-rijo.pdf",
    declarationLinkType: "direct_pdf",
    reportedAssets: 45184045.27,
    reportedLiabilities: 8761847.39,
    reportedNetWorth: 36422197.88,
    sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43659/rafael-baron-duluc-rijo.pdf",
    sourceLabel: "Declaración jurada oficial DJP-42237",
    priorDeclarationId: "39472",
    note: "Actualización por cambio de cargo. El formulario identifica como declaración anterior un cese de funciones ID 39472.",
  },
  "eduard-alexis-espiritusanto-castillo": {
    senatorId: "eduard-alexis-espiritusanto-castillo",
    declarationPeriod: "2024",
    declarationUrl: senateDeclarationPortal,
    declarationLinkType: "official_record",
    reportedAssets: 986781911.99,
    reportedLiabilities: 24000000,
    reportedNetWorth: 962781911.99,
    sourceUrl: "https://www.camaradecuentas.gob.do/index.php/reportes-djp/category/24-listado-de-funcionarios-que-entregaron-su-declaracion-extemporanea?download=1955%3Aextemporaneas-procuraduria-al-25-10-2024",
    sourceLabel: "Cámara de Cuentas · listado de declaraciones extemporáneas",
    note: "La Cámara de Cuentas registra entrega el 04/10/2024. El total patrimonial publicado posteriormente por Diario Libre permite mostrar activos/patrimonio neto mientras se resuelve el PDF individual.",
  },
  "ramon-rogelio-genao-duran": {
    senatorId: "ramon-rogelio-genao-duran",
    declarationPeriod: "2024",
    declarationUrl: senateDeclarationPortal,
    declarationLinkType: "official_portal",
    reportedAssets: 61863531.72,
    reportedLiabilities: 30025534.46,
    reportedNetWorth: 31837997.26,
    sourceUrl: dlPatrimony,
    sourceLabel: "Visualización de declaraciones juradas basada en Cámara de Cuentas · Diario Libre",
    note: "Reelecto. El OED buscará la declaración anterior compatible para medir evolución 2020→2024 con la misma metodología.",
  },
  "alexis-victoria-yeb": {
    senatorId: "alexis-victoria-yeb",
    declarationPeriod: "2024",
    declarationUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/41290/alexis-victoria-yeb.pdf",
    declarationLinkType: "direct_pdf",
    reportedAssets: 3928019156.42,
    reportedLiabilities: 237187634.36,
    reportedNetWorth: 3690831522.06,
    sourceUrl: "https://www.diariolibre.com/politica/gobierno/2024/10/09/entre-politica-y-negocios-las-fortunas-de-los-senadores-dominicanos/2875604",
    sourceLabel: "Diario Libre · análisis de declaración oficial Cámara de Cuentas",
    note: "La fuente reporta RD$3,928 millones en activos y más de RD$237 millones en deuda. El PDF oficial también documenta salario y asignaciones legislativas individuales.",
  },
};

export const first16PatrimonyIds = Object.keys(senatorPatrimonyFirst16);
