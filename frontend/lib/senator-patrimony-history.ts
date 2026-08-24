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

const listin2020 =
  "https://listindiario.com/la-republica/2020/09/19/635771/las-declaraciones-juradas-de-bienes-de-21-senadores.html";
const municipalCompliance =
  "https://www.camaradecuentas.gob.do/index.php/cumplimiento?download=1970%3Alistado-de-electos-reelectos-y-que-cesaron-a-nivel-municipal-2024-2028-que-no-han-presentado-su-declaracion-al-corte-de-14-11-2024";
const felixHistory = "https://pciudadana.org/wp-content/uploads/2022/03/Felix-Bautista.pdf";

export const senatorPatrimonyHistory: Record<string, SenatorPatrimonyHistoryPoint[]> = {
  "lia-ynocencia-diaz-santana": [
    {
      date: "2020",
      office: "Senadora por Azua",
      reportedAmount: 47533193.3,
      reportedAmountLabel: "Patrimonio/bienes publicados",
      reportedLiabilities: 13933262.7,
      sourceUrl: listin2020,
      sourceLabel: "Listín Diario · resumen de declaraciones juradas 2020",
      comparability: "partial",
    },
  ],
  "moises-ayala-perez": [
    {
      date: "declaración anterior ID 22964",
      office: "Cargo público anterior al Senado",
      sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43667/moises-ayala-perez.pdf",
      sourceLabel: "Declaración jurada oficial DJP-42469",
      comparability: "reference_only",
      note: "La declaración de 2024 identifica expresamente una declaración anterior rectificativa ID 22964. Falta recuperar y normalizar el formulario previo para cuantificar la variación.",
    },
  ],
  "manuel-maria-rodriguez-ortega": [
    {
      date: "2020-2024",
      office: "Alcalde de Loma de Cabrera",
      sourceUrl: municipalCompliance,
      sourceLabel: "Cámara de Cuentas · cumplimiento DJP municipal",
      comparability: "reference_only",
      note: "La declaración senatorial 2024 identifica una declaración anterior ID 21678.",
    },
  ],
  "franklin-martin-romero-morillo": [
    {
      date: "2016-09-13",
      office: "Diputado por Duarte",
      sourceUrl: "https://bibliotecadelcongreso.gob.do/Libros/InformeProvDuarte_2019-2020.pdf",
      sourceLabel: "Cámara de Diputados · Informe de Gestión 2019-2020",
      comparability: "reference_only",
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
    },
  ],
  "santiago-jose-zorrilla": [
    {
      date: "2020",
      office: "Senador por El Seibo",
      reportedAssets: 155000000,
      sourceUrl: "https://www.diariolibre.com/politica/gobierno/2024/09/25/santiago-zorrilla-aclara-sobre-declaracion-de-bienes/2861201",
      sourceLabel: "Diario Libre · aclaración patrimonial 2020-2024",
      comparability: "partial",
      note: "La serie publicada sitúa los activos de 2020 alrededor de RD$155 millones y los de 2024 alrededor de RD$181 millones.",
    },
  ],
  "cristobal-venerado-castillo-liriano": [
    {
      date: "2020",
      office: "Senador por Hato Mayor",
      reportedAmount: 403948101,
      reportedAmountLabel: "Patrimonio/bienes publicados",
      reportedLiabilities: 12023860,
      sourceUrl: listin2020,
      sourceLabel: "Listín Diario · resumen de declaraciones juradas 2020",
      comparability: "partial",
    },
  ],
  "maria-mercedes-ortiz-dilone": [
    {
      date: "2020-2024",
      office: "Alcaldesa de Salcedo",
      sourceUrl: municipalCompliance,
      sourceLabel: "Cámara de Cuentas · cumplimiento DJP municipal",
      comparability: "reference_only",
    },
  ],
  "rafael-baron-duluc-rijo": [
    {
      date: "declaración anterior ID 39472",
      office: "Cargo público anterior",
      sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43659/rafael-baron-duluc-rijo.pdf",
      sourceLabel: "Declaración jurada oficial DJP-42237",
      comparability: "reference_only",
      note: "La declaración vigente identifica una declaración anterior de cese de funciones ID 39472. Falta recuperar el formulario previo para normalizar activos, pasivos y patrimonio neto.",
    },
  ],
  "ramon-rogelio-genao-duran": [
    {
      date: "2020",
      office: "Senador por La Vega",
      reportedAmount: 70714130.9,
      reportedAmountLabel: "Patrimonio/bienes publicados",
      reportedLiabilities: 37710109,
      sourceUrl: listin2020,
      sourceLabel: "Listín Diario · resumen de declaraciones juradas 2020",
      comparability: "partial",
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
      note: "La fuente reporta patrimonio neto de RD$1,977 millones en 2020 y alrededor de RD$3,696 millones en 2024.",
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
      note: "La fuente fija RD$23,751,235 en 2020 y RD$27,472,119 en 2024.",
    },
  ],
  "ginnette-altagracia-bournigal": [
    {
      date: "2020",
      office: "Senadora por Puerto Plata",
      sourceUrl: "https://transparencia.senadord.gob.do/wp-content/uploads/wpfd/preview_files/GINNETTE-ALTAGRACIA-BOURNIGAL-JIMENEZ%282d0ecff3cc32fb5d6de6590072b79abd%29.pdf",
      sourceLabel: "Declaración jurada oficial DJP-026498",
      comparability: "reference_only",
    },
  ],
  "pedro-manuel-catrain-bonilla": [
    {
      date: "2020",
      office: "Senador por Samaná",
      reportedAmount: 192280127,
      reportedAmountLabel: "Patrimonio/bienes publicados",
      reportedLiabilities: 12237494.4,
      sourceUrl: listin2020,
      sourceLabel: "Listín Diario · resumen de declaraciones juradas 2020",
      comparability: "partial",
    },
  ],
  "gustavo-lara-salazar": [
    {
      date: "declaración anterior ID 25086",
      office: "Cargo público anterior",
      sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43663/gustavo-lara-salazar.pdf",
      sourceLabel: "Declaración jurada oficial DJP-42676",
      comparability: "reference_only",
      note: "La declaración de 2024 identifica una declaración anterior ID 25086. Falta recuperar el formulario previo para calcular evolución comparable.",
    },
  ],
  "milciades-aneudy-ortiz-sajiun": [
    {
      date: "2020-2024",
      office: "Alcalde de San José de Ocoa",
      sourceUrl: municipalCompliance,
      sourceLabel: "Cámara de Cuentas · cumplimiento DJP municipal",
      comparability: "reference_only",
      note: "La declaración senatorial 2024 identifica una declaración anterior ID 19335.",
    },
  ],
  "felix-ramon-bautista-rosario": [
    {
      date: "1996-08",
      office: "Subdirector de la Oficina Coordinadora y Fiscalizadora de Obras del Estado",
      reportedNetWorth: 547000,
      sourceUrl: felixHistory,
      sourceLabel: "Participación Ciudadana · recopilación histórica",
      comparability: "comparable",
    },
    {
      date: "2005-04",
      office: "Director de OISOE",
      reportedAssets: 9667000,
      reportedLiabilities: 2900000,
      reportedNetWorth: 6767000,
      sourceUrl: felixHistory,
      sourceLabel: "Participación Ciudadana · recopilación histórica",
      comparability: "comparable",
    },
    {
      date: "2008-12",
      office: "Director de OISOE",
      reportedNetWorth: 10000000,
      sourceUrl: felixHistory,
      sourceLabel: "Participación Ciudadana · recopilación histórica",
      comparability: "comparable",
    },
    {
      date: "2010-11",
      office: "Senador por San Juan",
      reportedNetWorth: 16100000,
      sourceUrl: felixHistory,
      sourceLabel: "Participación Ciudadana · recopilación histórica",
      comparability: "comparable",
    },
    {
      date: "2020",
      office: "Senador por San Juan",
      reportedAmount: 27869001.8,
      reportedAmountLabel: "Patrimonio publicado",
      reportedLiabilities: 24680106,
      sourceUrl: listin2020,
      sourceLabel: "Listín Diario · resumen de declaraciones juradas 2020",
      comparability: "partial",
    },
  ],
  "ricardo-de-los-santos-polanco": [
    {
      date: "2020-2024",
      office: "Senador por Sánchez Ramírez",
      sourceUrl: "https://memoriahistorica.senadord.gob.do/items/23f0c4e3-4ece-4e20-9c5d-bab611de4e1b",
      sourceLabel: "Memoria Histórica del Senado",
      comparability: "reference_only",
    },
  ],
  "daniel-enrique-rivera-reyes": [
    {
      date: "declaración anterior ID 30193",
      office: "Ministro de Salud Pública",
      sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43664/daniel-enrique-de-jesus-rivera-reyes.pdf",
      sourceLabel: "Declaración jurada oficial DJP-41346",
      comparability: "reference_only",
      note: "La declaración senatorial de 2024 identifica una declaración anterior rectificativa ID 30193 y registra su antecedente como ministro de Salud Pública 2021-2024.",
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
      sourceLabel: "Diario Libre · declaración jurada 2020",
      comparability: "comparable",
    },
  ],
  "odalis-rafael-rodriguez-rodriguez": [
    {
      date: "declaración anterior ID 20129",
      office: "Alcalde de Mao / cargo público anterior",
      sourceUrl: "https://transparencia.senadord.gob.do/download/187/declaraciones-juradas/43675/odalis-rafael-rodriguez-rodriguez.pdf",
      sourceLabel: "Declaración jurada oficial DJP-42196",
      comparability: "reference_only",
      note: "La declaración de 2024 identifica una declaración anterior rectificativa ID 20129. El expediente vigente también documenta antecedentes como alcalde de Mao.",
    },
  ],
};

export const senatorsWithHistoricalPatrimony = Object.keys(senatorPatrimonyHistory);
