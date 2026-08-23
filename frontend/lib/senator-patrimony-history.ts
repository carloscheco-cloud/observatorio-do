export type SenatorPatrimonyHistoryPoint = {
  date: string;
  office?: string;
  reportedAssets?: number;
  reportedLiabilities?: number;
  reportedNetWorth?: number;
  reportedAmount?: number;
  reportedAmountLabel?: string;
  sourceUrl: string;
  sourceLabel: string;
  comparability: "comparable" | "partial" | "reference_only";
  note?: string;
};

/**
 * Historical patrimony points located before the current 2024 Senate snapshot.
 * A point is marked `comparable` only when the source gives a sufficiently clear
 * assets/liabilities/net-worth interpretation. `partial` preserves useful older
 * declarations without forcing unlike totals into a false growth calculation.
 */
export const senatorPatrimonyHistory: Record<string, SenatorPatrimonyHistoryPoint[]> = {
  "lia-ynocencia-diaz-santana": [
    {
      date: "2020",
      office: "Senadora por Azua",
      reportedAmount: 47533193.3,
      reportedAmountLabel: "Patrimonio/bienes publicados",
      reportedLiabilities: 13933262.7,
      sourceUrl: "https://listindiario.com/la-republica/2020/09/19/635771/las-declaraciones-juradas-de-bienes-de-21-senadores.html",
      sourceLabel: "Listín Diario · resumen de declaraciones juradas 2020",
      comparability: "partial",
      note: "La nota de 2020 publica patrimonio/bienes y deudas, pero no usa una semántica suficientemente uniforme para recalcular patrimonio neto con plena comparabilidad frente a 2024.",
    },
  ],
  "manuel-maria-rodriguez-ortega": [
    {
      date: "2020-2024",
      office: "Alcalde de Loma de Cabrera",
      sourceUrl: "https://www.camaradecuentas.gob.do/index.php/cumplimiento?download=1970%3Alistado-de-electos-reelectos-y-que-cesaron-a-nivel-municipal-2024-2028-que-no-han-presentado-su-declaracion-al-corte-de-14-11-2024",
      sourceLabel: "Cámara de Cuentas · listado de cumplimiento DJP municipal",
      comparability: "reference_only",
      note: "La Cámara de Cuentas lo registra como alcalde 2020-2024 y señala omisión de la declaración de cese al corte del 14/11/2024. Su declaración senatorial 2024 identifica una declaración anterior ID 21678.",
    },
  ],
  "franklin-martin-romero-morillo": [
    {
      date: "2016-09-13",
      office: "Diputado por Duarte",
      sourceUrl: "https://bibliotecadelcongreso.gob.do/Libros/InformeProvDuarte_2019-2020.pdf",
      sourceLabel: "Cámara de Diputados · Informe de Gestión 2019-2020",
      comparability: "reference_only",
      note: "El informe reproduce la constancia de recepción de su declaración jurada como diputado, presentada el 13/09/2016. El monto no queda legible en la constancia consultada.",
    },
    {
      date: "2020-09",
      office: "Senador por Duarte",
      reportedAmount: 446851091.214,
      reportedAmountLabel: "Bienes/patrimonio publicado",
      reportedLiabilities: 39704120,
      sourceUrl: "https://www.diariolibre.com/actualidad/senador-franklin-romero-morillo-declara-fortuna-de-mas-de-446-millones-de-pesos-FH21516993",
      sourceLabel: "Diario Libre · declaración jurada 2020",
      comparability: "partial",
      note: "La publicación reporta RD$446.85 millones y pasivos por RD$39.70 millones. Se conserva como punto histórico sin forzar equivalencia exacta con el total 2024 hasta normalizar ambos formularios.",
    },
  ],
  "santiago-jose-zorrilla": [
    {
      date: "2020",
      office: "Senador por El Seibo",
      reportedAssets: 155000000,
      sourceUrl: "https://www.diariolibre.com/politica/gobierno/2024/09/25/santiago-zorrilla-aclara-sobre-declaracion-de-bienes/2861201",
      sourceLabel: "Diario Libre · aclaración del senador con cuadro 2020-2024",
      comparability: "comparable",
      note: "La aclaración del propio senador sitúa sus activos de 2020 en más de RD$154 millones y los de 2024 en aproximadamente RD$181 millones, un incremento cercano a RD$26 millones. Otras notas de 2020 sumaron conceptos de forma distinta; el OED usa esta serie para no mezclar activos y pasivos.",
    },
  ],
  "cristobal-venerado-castillo-liriano": [
    {
      date: "2020",
      office: "Senador por Hato Mayor",
      reportedAmount: 403948101,
      reportedAmountLabel: "Patrimonio/bienes publicados",
      reportedLiabilities: 12023860,
      sourceUrl: "https://listindiario.com/la-republica/2020/09/19/635771/las-declaraciones-juradas-de-bienes-de-21-senadores.html",
      sourceLabel: "Listín Diario · resumen de declaraciones juradas 2020",
      comparability: "partial",
      note: "La publicación de 2020 reporta RD$403.95 millones y RD$12.02 millones en deudas/gastos. Se mantiene como referencia histórica hasta normalizar el formulario original.",
    },
  ],
  "maria-mercedes-ortiz-dilone": [
    {
      date: "2020-2024",
      office: "Alcaldesa de Salcedo",
      sourceUrl: "https://www.camaradecuentas.gob.do/index.php/cumplimiento?download=1970%3Alistado-de-electos-reelectos-y-que-cesaron-a-nivel-municipal-2024-2028-que-no-han-presentado-su-declaracion-al-corte-de-14-11-2024",
      sourceLabel: "Cámara de Cuentas · listado de cumplimiento DJP municipal",
      comparability: "reference_only",
      note: "La Cámara de Cuentas la identifica como alcaldesa 2020-2024 y registra omisión de declaración de cese al corte del 14/11/2024. Falta localizar un monto histórico compatible.",
    },
  ],
  "ramon-rogelio-genao-duran": [
    {
      date: "2020",
      office: "Senador por La Vega",
      reportedAmount: 70714130.9,
      reportedAmountLabel: "Patrimonio/bienes publicados",
      reportedLiabilities: 37710109,
      sourceUrl: "https://listindiario.com/la-republica/2020/09/19/635771/las-declaraciones-juradas-de-bienes-de-21-senadores.html",
      sourceLabel: "Listín Diario · resumen de declaraciones juradas 2020",
      comparability: "partial",
      note: "La nota publica RD$70.71 millones y deudas/gastos por RD$37.71 millones. La comparación con 2024 se muestra como referencia hasta normalizar el formulario de 2020.",
    },
  ],
  "alexis-victoria-yeb": [
    {
      date: "2020",
      office: "Senador por María Trinidad Sánchez",
      reportedAssets: 2147000000,
      reportedNetWorth: 1977000000,
      sourceUrl: "https://noticiassin.com/patrimonio-del-senador-alexis-victoria-yeb-casi-se-duplica-entre-2020-y-2024/?amp=1",
      sourceLabel: "Noticias SIN · comparación de declaraciones 2020-2024",
      comparability: "comparable",
      note: "La fuente compara la misma serie: activos de RD$2,147 millones en 2020 y RD$4,030 millones en 2024; patrimonio neto de RD$1,977 millones a RD$3,696 millones (+86.93%). El snapshot 2024 del OED usa el PDF vigente y puede diferir ligeramente por fecha/cálculo.",
    },
  ],
  "hector-elpidio-acosta-restituyo": [
    {
      date: "2020-09",
      office: "Senador por Monseñor Nouel",
      reportedAssets: 85000000,
      reportedLiabilities: 20900000,
      sourceUrl: "https://listindiario.com/entretenimiento/2020/09/03/633669/hector-acosta-declara-bienes-por-unos-85-millones-de-pesos.html",
      sourceLabel: "Listín Diario · declaración jurada 2020",
      comparability: "partial",
      note: "La nota reporta al menos RD$85 millones en bienes, más US$43,000 en una cuenta en EE. UU.; entre los pasivos identifica RD$17.5 millones hipotecarios y RD$3.4 millones personales. La cuenta en dólares se mantiene separada.",
    },
  ],
  "julito-fulcar-encarnacion": [
    {
      date: "2020",
      office: "Diputado por Peravia",
      reportedNetWorth: 23751235,
      sourceUrl: "https://noticiassin.com/de-la-camara-de-diputados-al-senado-julito-furcal-presenta-patrimonio-de-rd27-5-mm/",
      sourceLabel: "Noticias SIN · comparación de declaraciones 2020-2024",
      comparability: "comparable",
      note: "La publicación corregida fija RD$23,751,235 en 2020 y RD$27,472,119 en 2024, un aumento de RD$3,720,884.",
    },
  ],
  "ginnette-altagracia-bournigal": [
    {
      date: "2020",
      office: "Senadora por Puerto Plata",
      sourceUrl: "https://transparencia.senadord.gob.do/wp-content/uploads/wpfd/preview_files/GINNETTE-ALTAGRACIA-BOURNIGAL-JIMENEZ%282d0ecff3cc32fb5d6de6590072b79abd%29.pdf",
      sourceLabel: "Declaración jurada oficial DJP-026498",
      comparability: "reference_only",
      note: "PDF oficial histórico localizado. Es declaración rectificativa del período iniciado el 16/08/2020 y referencia una actualización anterior ID 23936. Falta normalizar el total de activos/pasivos del documento.",
    },
  ],
  "pedro-manuel-catrain-bonilla": [
    {
      date: "2020",
      office: "Senador por Samaná",
      reportedAmount: 192280127,
      reportedAmountLabel: "Patrimonio/bienes publicados",
      reportedLiabilities: 12237494.4,
      sourceUrl: "https://listindiario.com/la-republica/2020/09/19/635771/las-declaraciones-juradas-de-bienes-de-21-senadores.html",
      sourceLabel: "Listín Diario · resumen de declaraciones juradas 2020",
      comparability: "partial",
      note: "La publicación reporta RD$192.28 millones y RD$12.24 millones en deudas/gastos. El 2024 del OED usa un patrimonio neto corregido de RD$188.26 millones; se evita calcular variación porcentual hasta normalizar 2020.",
    },
  ],
  "milciades-aneudy-ortiz-sajiun": [
    {
      date: "2020-2024",
      office: "Alcalde de San José de Ocoa",
      sourceUrl: "https://www.camaradecuentas.gob.do/index.php/cumplimiento?download=1970%3Alistado-de-electos-reelectos-y-que-cesaron-a-nivel-municipal-2024-2028-que-no-han-presentado-su-declaracion-al-corte-de-14-11-2024",
      sourceLabel: "Cámara de Cuentas · listado de cumplimiento DJP municipal",
      comparability: "reference_only",
      note: "La Cámara de Cuentas lo registra como alcalde 2020-2024 y con omisión de declaración de cese al corte del 14/11/2024. Su declaración senatorial 2024 identifica una declaración anterior ID 19335.",
    },
  ],
  "felix-ramon-bautista-rosario": [
    {
      date: "1996-08",
      office: "Subdirector de la Oficina Coordinadora y Fiscalizadora de Obras del Estado",
      reportedNetWorth: 547000,
      sourceUrl: "https://pciudadana.org/wp-content/uploads/2022/03/Felix-Bautista.pdf",
      sourceLabel: "Participación Ciudadana · recopilación de declaraciones juradas y expediente público",
      comparability: "comparable",
      note: "El documento señala que, según su propia declaración jurada, al ingresar a la administración pública declaró RD$547 mil.",
    },
    {
      date: "2005-04",
      office: "Director de OISOE",
      reportedAssets: 9667000,
      reportedLiabilities: 2900000,
      reportedNetWorth: 6767000,
      sourceUrl: "https://pciudadana.org/wp-content/uploads/2022/03/Felix-Bautista.pdf",
      sourceLabel: "Participación Ciudadana · recopilación de declaraciones juradas y expediente público",
      comparability: "comparable",
      note: "El documento resume activos de RD$9.667 millones, pasivos de RD$2.9 millones y patrimonio neto de RD$6.767 millones; además menciona US$8,000 en ahorro, mantenidos aparte.",
    },
    {
      date: "2008-12",
      office: "Director de OISOE",
      reportedNetWorth: 10000000,
      sourceUrl: "https://pciudadana.org/wp-content/uploads/2022/03/Felix-Bautista.pdf",
      sourceLabel: "Participación Ciudadana · recopilación de declaraciones juradas y expediente público",
      comparability: "comparable",
      note: "La declaración renovada de diciembre de 2008 consignó aproximadamente RD$10 millones.",
    },
    {
      date: "2010-11",
      office: "Senador por San Juan",
      reportedNetWorth: 16100000,
      sourceUrl: "https://pciudadana.org/wp-content/uploads/2022/03/Felix-Bautista.pdf",
      sourceLabel: "Participación Ciudadana · recopilación de declaraciones juradas y expediente público",
      comparability: "comparable",
      note: "Al asumir como senador en 2010, la declaración presentada en noviembre consignó RD$16.1 millones.",
    },
    {
      date: "2020",
      office: "Senador por San Juan",
      reportedAmount: 27869001.8,
      reportedAmountLabel: "Patrimonio publicado",
      reportedLiabilities: 24680106,
      sourceUrl: "https://listindiario.com/la-republica/2020/09/19/635771/las-declaraciones-juradas-de-bienes-de-21-senadores.html",
      sourceLabel: "Listín Diario · resumen de declaraciones juradas 2020",
      comparability: "partial",
      note: "La publicación de 2020 reporta RD$27.87 millones y deudas/gastos por RD$24.68 millones. El salto a 2024 debe compararse solo después de normalizar el formulario 2020.",
    },
  ],
  "ricardo-de-los-santos-polanco": [
    {
      date: "2020-2024",
      office: "Senador por Sánchez Ramírez",
      sourceUrl: "https://memoriahistorica.senadord.gob.do/items/23f0c4e3-4ece-4e20-9c5d-bab611de4e1b",
      sourceLabel: "Memoria Histórica del Senado · ficha 2020-2024",
      comparability: "reference_only",
      note: "Está confirmado como senador del período 2020-2024. Aún falta localizar un monto histórico verificable de su declaración jurada para compararlo con el total publicado de 2024.",
    },
  ],
  "antonio-manuel-taveras-guzman": [
    {
      date: "2020-09",
      office: "Senador por Santo Domingo",
      reportedAssets: 648912405.38,
      reportedLiabilities: 115442672.53,
      reportedNetWorth: 533469732,
      sourceUrl: "https://www.diariolibre.com/actualidad/politica/senador-antonio-taveras-declara-una-fortuna-de-mas-de-rd-533-millones-CE21520046",
      sourceLabel: "Diario Libre · declaración jurada 2020 normalizada a tasa RD$59/US$",
      comparability: "comparable",
      note: "La fuente convierte los activos en dólares a una tasa de RD$59/US$ y obtiene activos totales de RD$648.91 millones, deudas de RD$115.44 millones y patrimonio neto de RD$533.47 millones. El OED conserva la tasa usada por la fuente para este punto histórico.",
    },
  ],
  "odalis-rafael-rodriguez-rodriguez": [
    {
      date: "2020-2024",
      office: "Alcalde de Mao",
      sourceUrl: "https://www.camaradecuentas.gob.do/index.php/cumplimiento?download=1970%3Alistado-de-electos-reelectos-y-que-cesaron-a-nivel-municipal-2024-2028-que-no-han-presentado-su-declaracion-al-corte-de-14-11-2024",
      sourceLabel: "Cámara de Cuentas · listado de cumplimiento DJP municipal",
      comparability: "reference_only",
      note: "La Cámara de Cuentas lo registra como alcalde de Mao 2020-2024 y con omisión de declaración de cese al corte del 14/11/2024. El OED mantiene esta información como evento de cumplimiento, no como monto patrimonial.",
    },
  ],
};

export const senatorsWithHistoricalPatrimony = Object.keys(senatorPatrimonyHistory);
