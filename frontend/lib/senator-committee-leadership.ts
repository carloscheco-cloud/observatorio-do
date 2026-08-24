export type SenatorCommitteeLeadership = {
  committee: string;
  role: "presidente" | "vicepresidente" | "secretario";
  period: string;
  sourceUrl: string;
};

const sourceUrl = "https://www.senadord.gob.do/comisiones/lista-de-comisiones/";
const period = "agosto 2024 – agosto 2026";

/**
 * Roles directivos publicados en el listado oficial de comisiones permanentes.
 * No se infieren identidades cuando el portal presenta un nombre inconsistente.
 */
export const senatorCommitteeLeadership: Record<string, SenatorCommitteeLeadership[]> = {
  "ricardo-de-los-santos-polanco": [{ committee: "Administración Interior", role: "presidente", period, sourceUrl }],
  "pedro-manuel-catrain-bonilla": [
    { committee: "Administración Interior", role: "vicepresidente", period, sourceUrl },
    { committee: "Hacienda", role: "presidente", period, sourceUrl },
  ],
  "lia-ynocencia-diaz-santana": [
    { committee: "Administración Interior", role: "secretario", period, sourceUrl },
    { committee: "Asuntos de la Familia y Equidad de Género", role: "vicepresidente", period, sourceUrl },
    { committee: "Salud Pública", role: "presidente", period, sourceUrl },
    { committee: "Seguridad Social, Trabajo y Pensiones", role: "secretario", period, sourceUrl },
  ],
  "aracelis-villanueva-figueroa": [
    { committee: "Administración Interior", role: "secretario", period, sourceUrl },
    { committee: "Asuntos de la Familia y Equidad de Género", role: "presidente", period, sourceUrl },
    { committee: "Deportes", role: "secretario", period, sourceUrl },
    { committee: "Presupuesto", role: "vicepresidente", period, sourceUrl },
  ],
  "manuel-maria-rodriguez-ortega": [
    { committee: "Asuntos Agropecuarios y Agroindustriales", role: "presidente", period, sourceUrl },
    { committee: "Asuntos Fronterizos", role: "secretario", period, sourceUrl },
    { committee: "Deportes", role: "vicepresidente", period, sourceUrl },
  ],
  "milciades-aneudy-ortiz-sajiun": [
    { committee: "Asuntos Agropecuarios y Agroindustriales", role: "vicepresidente", period, sourceUrl },
    { committee: "Desarrollo Municipal y ONG", role: "presidente", period, sourceUrl },
    { committee: "Juventud", role: "secretario", period, sourceUrl },
  ],
  "eduard-alexis-espiritusanto-castillo": [
    { committee: "Asuntos Agropecuarios y Agroindustriales", role: "secretario", period, sourceUrl },
    { committee: "Juventud", role: "presidente", period, sourceUrl },
    { committee: "Turismo", role: "vicepresidente", period, sourceUrl },
  ],
  "santiago-jose-zorrilla": [
    { committee: "Asuntos Energéticos", role: "presidente", period, sourceUrl },
    { committee: "Recursos Naturales y Medio Ambiente", role: "secretario", period, sourceUrl },
    { committee: "Relaciones Exteriores y Cooperación Internacional", role: "vicepresidente", period, sourceUrl },
  ],
  "ramon-rogelio-genao-duran": [
    { committee: "Asuntos Energéticos", role: "vicepresidente", period, sourceUrl },
    { committee: "Industria, Comercio y Zonas Francas", role: "secretario", period, sourceUrl },
    { committee: "Seguimiento, Control y Evaluación de la Agenda Parlamentaria", role: "presidente", period, sourceUrl },
  ],
  "pedro-antonio-tineo-nunez": [
    { committee: "Asuntos Energéticos", role: "secretario", period, sourceUrl },
    { committee: "Dominicanos Residentes en el Exterior", role: "vicepresidente", period, sourceUrl },
    { committee: "Presupuesto", role: "presidente", period, sourceUrl },
    { committee: "Transporte y Telecomunicaciones", role: "vicepresidente", period, sourceUrl },
  ],
  "maria-mercedes-ortiz-dilone": [
    { committee: "Asuntos de la Familia y Equidad de Género", role: "secretario", period, sourceUrl },
    { committee: "Desarrollo Municipal y ONG", role: "vicepresidente", period, sourceUrl },
    { committee: "Relaciones Exteriores y Cooperación Internacional", role: "presidente", period, sourceUrl },
  ],
  "bernardo-aleman-rodriguez": [
    { committee: "Asuntos Fronterizos", role: "presidente", period, sourceUrl },
    { committee: "Economía, Planificación y Desarrollo", role: "secretario", period, sourceUrl },
  ],
  "jonhson-encarnacion-diaz": [
    { committee: "Contratos", role: "presidente", period, sourceUrl },
    { committee: "Dominicanos Residentes en el Exterior", role: "secretario", period, sourceUrl },
    { committee: "Salud Pública", role: "secretario", period, sourceUrl },
  ],
  "odalis-rafael-rodriguez-rodriguez": [
    { committee: "Contratos", role: "vicepresidente", period, sourceUrl },
    { committee: "Defensa y Seguridad Nacional", role: "secretario", period, sourceUrl },
    { committee: "Ética", role: "presidente", period, sourceUrl },
  ],
  "casimiro-antonio-marte-familia": [
    { committee: "Contratos", role: "secretario", period, sourceUrl },
    { committee: "Defensa y Seguridad Nacional", role: "vicepresidente", period, sourceUrl },
    { committee: "Obras Públicas", role: "secretario", period, sourceUrl },
    { committee: "Recursos Naturales y Medio Ambiente", role: "presidente", period, sourceUrl },
  ],
  "carlos-manuel-gomez-urena": [
    { committee: "Cultura", role: "presidente", period, sourceUrl },
    { committee: "Recursos Naturales y Medio Ambiente", role: "vicepresidente", period, sourceUrl },
    { committee: "Relaciones Exteriores y Cooperación Internacional", role: "secretario", period, sourceUrl },
  ],
  "franklin-martin-romero-morillo": [
    { committee: "Cultura", role: "vicepresidente", period, sourceUrl },
    { committee: "Interior y Policía y Seguridad Ciudadana", role: "presidente", period, sourceUrl },
    { committee: "Seguimiento, Control y Evaluación de la Agenda Parlamentaria", role: "secretario", period, sourceUrl },
  ],
  "hector-elpidio-acosta-restituyo": [
    { committee: "Cultura", role: "secretario", period, sourceUrl },
    { committee: "Modernización y Reforma", role: "vicepresidente", period, sourceUrl },
  ],
  "dagoberto-rodriguez-adames": [
    { committee: "Defensa y Seguridad Nacional", role: "presidente", period, sourceUrl },
    { committee: "Seguridad Social, Trabajo y Pensiones", role: "vicepresidente", period, sourceUrl },
    { committee: "Transporte y Telecomunicaciones", role: "secretario", period, sourceUrl },
  ],
  "gustavo-lara-salazar": [
    { committee: "Deportes", role: "presidente", period, sourceUrl },
    { committee: "Juventud", role: "vicepresidente", period, sourceUrl },
  ],
  "cristobal-venerado-castillo-liriano": [
    { committee: "Desarrollo Municipal y ONG", role: "secretario", period, sourceUrl },
    { committee: "Interior y Policía y Seguridad Ciudadana", role: "vicepresidente", period, sourceUrl },
    { committee: "Modernización y Reforma", role: "presidente", period, sourceUrl },
  ],
  "omar-leonel-fernandez-dominguez": [
    { committee: "Dominicanos Residentes en el Exterior", role: "presidente", period, sourceUrl },
    { committee: "Industria, Comercio y Zonas Francas", role: "vicepresidente", period, sourceUrl },
    { committee: "Justicia y Derechos Humanos", role: "secretario", period, sourceUrl },
  ],
  "julito-fulcar-encarnacion": [
    { committee: "Educación", role: "presidente", period, sourceUrl },
    { committee: "Educación Superior, Ciencia y Tecnología", role: "vicepresidente", period, sourceUrl },
  ],
  "moises-ayala-perez": [
    { committee: "Educación", role: "vicepresidente", period, sourceUrl },
    { committee: "Economía, Planificación y Desarrollo", role: "presidente", period, sourceUrl },
    { committee: "Interior y Policía y Seguridad Ciudadana", role: "secretario", period, sourceUrl },
  ],
  "felix-ramon-bautista-rosario": [
    { committee: "Educación", role: "secretario", period, sourceUrl },
    { committee: "Economía, Planificación y Desarrollo", role: "vicepresidente", period, sourceUrl },
    { committee: "Obras Públicas", role: "presidente", period, sourceUrl },
  ],
  "rafael-baron-duluc-rijo": [
    { committee: "Educación Superior, Ciencia y Tecnología", role: "presidente", period, sourceUrl },
    { committee: "Justicia y Derechos Humanos", role: "vicepresidente", period, sourceUrl },
    { committee: "Turismo", role: "secretario", period, sourceUrl },
  ],
  "daniel-enrique-rivera-reyes": [
    { committee: "Educación Superior, Ciencia y Tecnología", role: "secretario", period, sourceUrl },
    { committee: "Salud Pública", role: "vicepresidente", period, sourceUrl },
    { committee: "Seguridad Social, Trabajo y Pensiones", role: "presidente", period, sourceUrl },
  ],
  "antonio-manuel-taveras-guzman": [
    { committee: "Ética", role: "vicepresidente", period, sourceUrl },
    { committee: "Justicia y Derechos Humanos", role: "presidente", period, sourceUrl },
  ],
  "ginnette-altagracia-bournigal": [
    { committee: "Ética", role: "secretario", period, sourceUrl },
    { committee: "Seguimiento, Control y Evaluación de la Agenda Parlamentaria", role: "vicepresidente", period, sourceUrl },
    { committee: "Turismo", role: "presidente", period, sourceUrl },
  ],
  "andres-guillermo-lama-perez": [
    { committee: "Hacienda", role: "vicepresidente", period, sourceUrl },
    { committee: "Presupuesto", role: "secretario", period, sourceUrl },
    { committee: "Transporte y Telecomunicaciones", role: "presidente", period, sourceUrl },
  ],
  "alexis-victoria-yeb": [
    { committee: "Hacienda", role: "secretario", period, sourceUrl },
    { committee: "Industria, Comercio y Zonas Francas", role: "presidente", period, sourceUrl },
    { committee: "Obras Públicas", role: "vicepresidente", period, sourceUrl },
  ],
};

export const senatorsWithCommitteeLeadership = Object.keys(senatorCommitteeLeadership);