export type LegislativeChamber = "senate" | "deputies";
export type EducationStatus = "verified" | "partial" | "not_found" | "pending";

export type EducationRecord = {
  level?: string;
  credential: string;
  institution?: string;
  status?: "completed" | "in_progress" | "incomplete" | "honorary";
  sourceUrl: string;
};

export type Legislator = {
  id: string;
  fullName: string;
  chamber: LegislativeChamber;
  province: string;
  constituency?: string;
  representation?: "provincial" | "national" | "exterior";
  party?: string;
  photoUrl?: string;
  officialProfileUrl: string;
  rosterSourceUrl: string;
  education: EducationRecord[];
  educationStatus: EducationStatus;
  educationNote?: string;
};

const senateRosterSource =
  "https://www.senadord.gob.do/senadores-reciben-certificados-de-elecciones-de-la-jce/";

const senatorEnrichment: Record<string, Partial<Legislator>> = {
  "lia-ynocencia-diaz-santana": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/azua/",
    educationStatus: "verified",
    education: [
      { level: "grado", credential: "Doctora en Medicina", institution: "Universidad Central del Este (UCE)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/azua/" },
      { level: "especialidad", credential: "Médico Pediatra", institution: "Hospital Materno Infantil San Lorenzo de Los Mina / UASD", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/azua/" },
      { level: "formación continua", credential: "Infectología Pediátrica; manejo y tratamiento del dengue", institution: "San Juan, Puerto Rico", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/azua/" },
    ],
  },
  "andres-guillermo-lama-perez": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/bahoruco/",
    educationStatus: "verified",
    education: [
      { level: "grado", credential: "Administración y Finanzas", institution: "Pontificia Universidad Católica Madre y Maestra (PUCMM)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/bahoruco/" },
      { level: "formación continua", credential: "Tecnología, manejo y procesamiento de datos; CSTA Training; manejo estadístico; Gestión de Procesos", institution: "PUCMM y otros programas citados por el perfil oficial", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/bahoruco/" },
    ],
  },
  "moises-ayala-perez": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/barahona/",
    educationStatus: "partial",
    education: [
      { level: "grado/especialidad", credential: "Medicina; especialidad en Ginecología, Oncología y Obstetricia", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/barahona/" },
      { level: "especialidad", credential: "Ginecología-Oncológica", institution: "Instituto de Oncología Dr. Heriberto Pieter / Liga Dominicana Contra el Cáncer", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/barahona/" },
      { level: "grado", credential: "Derecho (6.º cuatrimestre según perfil oficial)", institution: "Universidad de la Tercera Edad (UTE)", status: "in_progress", sourceUrl: "https://www.senadord.gob.do/provincia/barahona/" },
    ],
    educationNote: "El perfil oficial describe la formación médica y especialidades, pero no identifica la universidad del grado de Medicina.",
  },
  "manuel-maria-rodriguez-ortega": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/dajabon/",
    educationStatus: "partial",
    education: [
      { level: "primaria/secundaria", credential: "Estudios primarios y secundarios en distintos centros del municipio de Loma de Cabrera", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/dajabon/" },
    ],
    educationNote: "El perfil oficial no publica estudios universitarios ni técnicos adicionales.",
  },
  "omar-leonel-fernandez-dominguez": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/distrito-nacional/",
    educationStatus: "verified",
    education: [
      { level: "grado", credential: "Licenciatura en Derecho", institution: "Pontificia Universidad Católica Madre y Maestra (PUCMM)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/distrito-nacional/" },
      { level: "maestría", credential: "Máster en Derecho de los Negocios Internacionales", institution: "Boston University", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/distrito-nacional/" },
    ],
  },
  "franklin-martin-romero-morillo": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/duarte/",
    educationStatus: "verified",
    education: [
      { level: "secundaria/equivalencia", credential: "GED", institution: "Estados Unidos", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/duarte/" },
      { level: "grado", credential: "Derecho", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/duarte/" },
      { level: "maestría", credential: "Derecho Constitucional y Derecho Público", institution: "Universidad de Castilla-La Mancha", status: "in_progress", sourceUrl: "https://www.senadord.gob.do/provincia/duarte/" },
      { level: "maestría", credential: "Gestión Pública y Liderazgo, especialidad en Derecho Administrativo", institution: "Universidad Europea del Atlántico (UNEATLANTICO)", status: "in_progress", sourceUrl: "https://www.senadord.gob.do/provincia/duarte/" },
    ],
  },
  "santiago-jose-zorrilla": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/el-seibo/",
    educationStatus: "partial",
    education: [
      { level: "grado", credential: "Licenciatura en Derecho", institution: "Universidad Experimental Félix Adam (UNEFA)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/el-seibo/" },
      { level: "formación continua", credential: "Cursos y diplomados relacionados con Derecho", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/el-seibo/" },
    ],
    educationNote: "El perfil oficial no enumera individualmente los cursos y diplomados.",
  },
  "jonhson-encarnacion-diaz": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/elias-pina/",
    educationStatus: "verified",
    education: [
      { level: "grado", credential: "Doctor en Medicina", institution: "Universidad Autónoma de Santo Domingo (UASD)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/elias-pina/" },
      { level: "postgrado", credential: "Neurocirugía", institution: "Hospital Docente Universitario Dr. Darío Contreras / Hospital de La Timone, Marsella", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/elias-pina/" },
      { level: "entrenamiento", credential: "Cirugía de columna", institution: "Universidad de Río Piedras, Puerto Rico", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/elias-pina/" },
    ],
  },
  "carlos-manuel-gomez-urena": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/espaillat/",
    educationStatus: "not_found",
    education: [],
    educationNote: "El perfil oficial consultado describe su trayectoria empresarial y política, pero no publica formación académica verificable.",
  },
  "cristobal-venerado-castillo-liriano": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/hato-mayor/",
    educationStatus: "verified",
    education: [
      { level: "primaria", credential: "Estudios primarios", institution: "Colegio Nuestra Señora del Carmen y Escuela Bernardo Pichardo", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/hato-mayor/" },
      { level: "secundaria", credential: "Estudios secundarios", institution: "Liceo César Nicolás Penson", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/hato-mayor/" },
      { level: "grado", credential: "Doctor en Derecho", institution: "Universidad Central del Este (UCE)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/hato-mayor/" },
    ],
  },
  "maria-mercedes-ortiz-dilone": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/hermanas-mirabal/",
    educationStatus: "verified",
    education: [
      { level: "grado", credential: "Licenciatura en Derecho, Cum Laude", institution: "Universidad Autónoma de Santo Domingo (UASD)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/hermanas-mirabal/" },
      { level: "maestría", credential: "Derecho, Economía y Políticas Públicas", institution: "Instituto Universitario Ortega y Gasset / Universidad Complutense de Madrid", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/hermanas-mirabal/" },
      { level: "maestría", credential: "Administración Pública", institution: "Universidad Tecnológica de Santiago (UTESA)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/hermanas-mirabal/" },
      { level: "maestría", credential: "Derecho Administrativo y Gestión Municipal", institution: "Universidad de Castilla-La Mancha", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/hermanas-mirabal/" },
      { level: "formación continua", credential: "Diplomados en gerencia política y municipal", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/hermanas-mirabal/" },
    ],
  },
  "dagoberto-rodriguez-adames": {
    officialProfileUrl: "https://www.senadord.gob.do/Descargas/1411/publicaciones/55477/2da-edicion-rev-senado",
    educationStatus: "partial",
    education: [
      { level: "grado", credential: "Doctor en Medicina", institution: "Universidad Autónoma de Santo Domingo (UASD)", status: "completed", sourceUrl: "https://www.senadord.gob.do/Descargas/1411/publicaciones/55477/2da-edicion-rev-senado" },
      { level: "especialidad", credential: "Anestesiología pediátrica", status: "completed", sourceUrl: "https://www.senadord.gob.do/Descargas/1411/publicaciones/55477/2da-edicion-rev-senado" },
    ],
    educationNote: "La revista institucional confirma la especialidad, pero el extracto consultado no identifica la institución donde la cursó.",
  },
  "rafael-baron-duluc-rijo": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/la-altagracia/",
    educationStatus: "verified",
    education: [
      { level: "grado", credential: "Doctor en Derecho", institution: "Universidad Central del Este (UCE)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/la-altagracia/" },
      { level: "postgrado", credential: "Cursos de Derecho Constitucional, Derecho Civil-Contratos, Derecho Civil-Daños, Negociación y Arbitraje", institution: "Programas en Salamanca y Toledo, España", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/la-altagracia/" },
      { level: "maestría", credential: "Derecho Privado, Francés e Internacional", institution: "Université Paris-Panthéon-Assas (Paris II)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/la-altagracia/" },
      { level: "maestría", credential: "Derecho Constitucional y Libertades Fundamentales", institution: "IGLOBAL / Université Paris 1 Panthéon-Sorbonne", status: "in_progress", sourceUrl: "https://www.senadord.gob.do/provincia/la-altagracia/" },
      { level: "postgrado", credential: "Liderazgo para la Gestión Pública", institution: "Barna Management School", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/la-altagracia/" },
    ],
  },
  "eduard-alexis-espiritusanto-castillo": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/la-romana/",
    educationStatus: "partial",
    education: [
      { level: "estudios", credential: "Derecho; Administración de Empresas; Administración Pública; Derecho Parlamentario y Técnica Legislativa; Gerencia de Proyectos; Gerencia Política y Gestión de Gobierno", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/la-romana/" },
    ],
    educationNote: "El perfil oficial enumera áreas de estudio, pero no especifica instituciones, grados ni fechas.",
  },
  "ramon-rogelio-genao-duran": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/la-vega/",
    educationStatus: "partial",
    education: [
      { level: "grado", credential: "Ingeniero Forestal", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/la-vega/" },
      { level: "formación especializada", credential: "Dasonomía", institution: "Programa becado por el Gobierno de Alemania, cursado en Honduras", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/la-vega/" },
      { level: "formación continua", credential: "Plantaciones forestales; Agropecuaria; aprovechamiento y utilización forestal", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/la-vega/" },
    ],
    educationNote: "El perfil oficial no identifica la institución del grado de Ingeniería Forestal.",
  },
  "alexis-victoria-yeb": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/maria-trinidad-sanchez/",
    educationStatus: "verified",
    education: [
      { level: "grado", credential: "Licenciatura en Administración de Empresas", institution: "Instituto Tecnológico de Santo Domingo (INTEC)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/maria-trinidad-sanchez/" },
    ],
  },
  "hector-elpidio-acosta-restituyo": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/monsenor-nouel/",
    educationStatus: "not_found",
    education: [],
    educationNote: "El perfil oficial consultado describe su formación artística práctica y trayectoria musical, pero no publica estudios académicos formales verificables.",
  },
  "bernardo-aleman-rodriguez": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/montecristi/",
    educationStatus: "partial",
    education: [
      { level: "técnico", credential: "Estudios de informática", institution: "Samanel", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/montecristi/" },
      { level: "técnico", credential: "Técnico agrícola", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/montecristi/" },
    ],
  },
  "pedro-antonio-tineo-nunez": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/monte-plata/",
    educationStatus: "partial",
    education: [
      { level: "grado", credential: "Licenciatura en Derecho", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/monte-plata/" },
      { level: "grado", credential: "Licenciatura en Administración de Empresas", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/monte-plata/" },
      { level: "postgrado", credential: "Ciencias Políticas", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/monte-plata/" },
      { level: "formación técnica", credential: "Varios estudios técnicos en formación", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/monte-plata/" },
    ],
    educationNote: "El perfil oficial no identifica las instituciones de los grados y postgrado.",
  },
  "julito-fulcar-encarnacion": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/peravia/",
    educationStatus: "verified",
    education: [
      { level: "formación docente", credential: "Maestro Normal Primario", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/peravia/" },
      { level: "grado", credential: "Licenciatura en Educación", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/peravia/" },
      { level: "grado", credential: "Ingeniería Agronómica", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/peravia/" },
      { level: "especialidad", credential: "Planificación y Gestión Educativa", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/peravia/" },
      { level: "maestría", credential: "Educación orientada a la Planificación y Gestión Educativa", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/peravia/" },
      { level: "formación continua", credential: "Experto Dinamizador (Coaching grupal) y más de 150 diplomados/cursos", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/peravia/" },
      { level: "doctorado", credential: "Ciencias de la Educación", institution: "Universidad Santander de México", status: "in_progress", sourceUrl: "https://www.senadord.gob.do/provincia/peravia/" },
    ],
  },
  "ginnette-altagracia-bournigal": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/puerto-plata/",
    educationStatus: "partial",
    education: [
      { level: "secundaria", credential: "Bachiller en Ciencias Naturales", institution: "Colegio San José de Puerto Plata", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/puerto-plata/" },
      { level: "técnico", credential: "Secretariado", institution: "Escuela de la Cámara de Comercio de Puerto Plata", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/puerto-plata/" },
      { level: "estudios universitarios", credential: "Sociología", institution: "Universidad Católica de Ponce, Puerto Rico", status: "incomplete", sourceUrl: "https://www.senadord.gob.do/provincia/puerto-plata/" },
    ],
  },
  "pedro-manuel-catrain-bonilla": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/samana/",
    educationStatus: "verified",
    education: [
      { level: "grado", credential: "Doctor en Derecho", institution: "Universidad Autónoma de Santo Domingo (UASD)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/samana/" },
      { level: "postgrado", credential: "Sociología", institution: "Universidad de Roma, Italia", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/samana/" },
      { level: "maestría", credential: "Ciencias Políticas", institution: "Facultad Latinoamericana de Ciencias Sociales (FLACSO), México", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/samana/" },
      { level: "postgrado", credential: "Justicia y Procedimiento Constitucional", institution: "Universidad de Castilla-La Mancha, Toledo", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/samana/" },
    ],
  },
  "gustavo-lara-salazar": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/san-cristobal/",
    educationStatus: "partial",
    education: [
      { level: "grado", credential: "Ingeniería Civil", institution: "Universidad Autónoma de Santo Domingo (UASD)", status: "incomplete", sourceUrl: "https://www.senadord.gob.do/provincia/san-cristobal/" },
      { level: "formación continua", credential: "Programa de liderazgo", institution: "Instituto Tecnológico de Santo Domingo (INTEC)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-cristobal/" },
      { level: "formación continua", credential: "Programa de liderazgo", institution: "Acton Academy", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-cristobal/" },
    ],
    educationNote: "El perfil oficial dice que ingresó a Ingeniería Civil, sin afirmar que completó el grado.",
  },
  "milciades-aneudy-ortiz-sajiun": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/san-jose-de-ocoa/",
    educationStatus: "verified",
    education: [
      { level: "grado", credential: "Administración de Empresas", institution: "Universidad Acción Pro-Educación y Cultura (UNAPEC)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-jose-de-ocoa/" },
      { level: "técnico", credential: "Informática", institution: "Centro de Tecnología Universal (CENTU)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-jose-de-ocoa/" },
      { level: "formación internacional", credential: "Administración Política / International Visitor Leadership Program (IVLP)", institution: "Departamento de Estado de los Estados Unidos", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-jose-de-ocoa/" },
    ],
  },
  "felix-ramon-bautista-rosario": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/san-juan/",
    educationStatus: "verified",
    education: [
      { level: "grado", credential: "Ingeniería Civil", institution: "Universidad Autónoma de Santo Domingo (UASD)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-juan/" },
      { level: "grado", credential: "Derecho", institution: "Universidad del Caribe", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-juan/" },
      { level: "maestría", credential: "Administración y Políticas Públicas", institution: "Utah State University", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-juan/" },
      { level: "maestría", credential: "Ciencias Políticas", institution: "Universidad Nacional Pedro Henríquez Ureña (UNPHU)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-juan/" },
      { level: "maestría", credential: "Relaciones Internacionales", institution: "Universidad Nacional Pedro Henríquez Ureña (UNPHU)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-juan/" },
      { level: "maestría", credential: "Economía", institution: "Universidad del País Vasco", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-juan/" },
      { level: "maestría", credential: "Derecho Constitucional y Procesal Constitucional", institution: "Universidad Autónoma de Santo Domingo (UASD)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-juan/" },
      { level: "maestría", credential: "Derecho Electoral y de Partidos Políticos", institution: "Universidad de Castilla-La Mancha", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-juan/" },
      { level: "doctorado", credential: "Economía", institution: "Universidad del País Vasco", status: "in_progress", sourceUrl: "https://www.senadord.gob.do/provincia/san-juan/" },
    ],
  },
  "aracelis-villanueva-figueroa": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/san-pedro-de-macoris/",
    educationStatus: "partial",
    education: [
      { level: "grado", credential: "Derecho, Summa Cum Laude", institution: "Universidad Central del Este (UCE)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-pedro-de-macoris/" },
      { level: "estudios", credential: "Comunicación", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-pedro-de-macoris/" },
      { level: "diplomado", credential: "Seguridad Social", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/san-pedro-de-macoris/" },
    ],
    educationNote: "El perfil oficial no identifica institución ni grado específico para los estudios de Comunicación ni el diplomado.",
  },
  "ricardo-de-los-santos-polanco": {
    officialProfileUrl: "https://memoriahistorica.senadord.gob.do/items/8a4bd1e3-2a5c-4061-b3e4-989bf29bdc5f/full",
    photoUrl: "https://memoriahistorica.senadord.gob.do/bitstreams/6738e97e-6424-474b-95e1-46d7fd13cd53/download",
    educationStatus: "verified",
    education: [
      { level: "grado", credential: "Licenciatura en Administración de Empresas", institution: "Universidad de la Tercera Edad (UTE)", status: "completed", sourceUrl: "https://memoriahistorica.senadord.gob.do/items/8a4bd1e3-2a5c-4061-b3e4-989bf29bdc5f/full" },
      { level: "maestría", credential: "Comunicación Corporativa", institution: "TECH Universidad Tecnológica", status: "completed", sourceUrl: "https://memoriahistorica.senadord.gob.do/items/8a4bd1e3-2a5c-4061-b3e4-989bf29bdc5f/full" },
      { level: "maestría", credential: "Derecho Constitucional y Derecho Público: Derechos Fundamentales y Derechos Constitucionales", institution: "Universidad de Castilla-La Mancha", status: "in_progress", sourceUrl: "https://memoriahistorica.senadord.gob.do/items/8a4bd1e3-2a5c-4061-b3e4-989bf29bdc5f/full" },
    ],
  },
  "daniel-enrique-rivera-reyes": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/santiago/",
    educationStatus: "verified",
    education: [
      { level: "grado", credential: "Medicina", institution: "Pontificia Universidad Católica Madre y Maestra (PUCMM)", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/santiago/" },
      { level: "especialidad", credential: "Medicina Interna", institution: "Hospital Regional Universitario José María Cabral y Báez", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/santiago/" },
      { level: "formación especializada", credential: "Gestión y Planificación de Centros y Servicios Asistenciales", institution: "Universidad Católica San Antonio de Murcia", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/santiago/" },
      { level: "formación especializada", credential: "Medicina Crítica", institution: "Hospital ABC de México", status: "completed", sourceUrl: "https://www.senadord.gob.do/provincia/santiago/" },
    ],
  },
};

export const senators: Legislator[] = [
  ["lia-ynocencia-diaz-santana", "Lía Ynocencia Díaz Santana", "Azua", "PRM"],
  ["andres-guillermo-lama-perez", "Andrés Guillermo Lama Pérez", "Bahoruco", "PRM"],
  ["moises-ayala-perez", "Moisés Ayala Pérez", "Barahona", "PRM"],
  ["manuel-maria-rodriguez-ortega", "Manuel María Rodríguez Ortega", "Dajabón", "PRM"],
  ["omar-leonel-fernandez-dominguez", "Omar Leonel Fernández Domínguez", "Distrito Nacional", "FP"],
  ["franklin-martin-romero-morillo", "Franklin Martín Romero Morillo", "Duarte", "PRM"],
  ["santiago-jose-zorrilla", "Santiago José Zorrilla", "El Seibo", "PRM"],
  ["jonhson-encarnacion-diaz", "Jonhson Encarnación Díaz", "Elías Piña", "PRM"],
  ["carlos-manuel-gomez-urena", "Carlos Manuel Gómez Ureña", "Espaillat", "PRM"],
  ["cristobal-venerado-castillo-liriano", "Cristóbal Venerado Antonio Castillo Liriano", "Hato Mayor", "PRM"],
  ["maria-mercedes-ortiz-dilone", "María Mercedes Ortiz Diloné", "Hermanas Mirabal", "PRM"],
  ["dagoberto-rodriguez-adames", "Dagoberto Rodríguez Adames", "Independencia", "PRM"],
  ["rafael-baron-duluc-rijo", "Rafael Barón Duluc Rijo", "La Altagracia", "PRM"],
  ["eduard-alexis-espiritusanto-castillo", "Eduard Alexis Espiritusanto Castillo", "La Romana", "FP"],
  ["ramon-rogelio-genao-duran", "Ramón Rogelio Genao Durán", "La Vega", "PRSC"],
  ["alexis-victoria-yeb", "Alexis Victoria Yeb", "María Trinidad Sánchez", "PRM"],
  ["hector-elpidio-acosta-restituyo", "Héctor Elpidio Acosta Restituyo", "Monseñor Nouel", "PRM"],
  ["bernardo-aleman-rodriguez", "Bernardo Alemán Rodríguez", "Monte Cristi", "PRM"],
  ["pedro-antonio-tineo-nunez", "Pedro Antonio Tineo Núñez", "Monte Plata", "PRM"],
  ["secundino-velazquez-pimentel", "Secundino Velázquez Pimentel", "Pedernales", "PRM"],
  ["julito-fulcar-encarnacion", "Julito Fulcar Encarnación", "Peravia", "PRM"],
  ["ginnette-altagracia-bournigal", "Ginnette Altagracia Bournigal Socías de Jiménez", "Puerto Plata", "PRM"],
  ["pedro-manuel-catrain-bonilla", "Pedro Manuel Catrain Bonilla", "Samaná", "PRM"],
  ["gustavo-lara-salazar", "Gustavo Lara Salazar", "San Cristóbal", "PRM"],
  ["milciades-aneudy-ortiz-sajiun", "Milcíades Aneudy Ortiz Sajiun", "San José de Ocoa", "PRM"],
  ["felix-ramon-bautista-rosario", "Félix Ramón Bautista Rosario", "San Juan", "FP"],
  ["aracelis-villanueva-figueroa", "Aracelis Villanueva Figueroa", "San Pedro de Macorís", "PRM"],
  ["ricardo-de-los-santos-polanco", "Ricardo De Los Santos Polanco", "Sánchez Ramírez", "PRM"],
  ["daniel-enrique-rivera-reyes", "Daniel Enrique de Jesús Rivera Reyes", "Santiago", "PRM"],
  ["casimiro-antonio-marte-familia", "Casimiro Antonio Marte Familia", "Santiago Rodríguez", "PRSC"],
  ["antonio-manuel-taveras-guzman", "Antonio Manuel Taveras Guzmán", "Santo Domingo", "Independiente"],
  ["odalis-rafael-rodriguez-rodriguez", "Odalis Rafael Rodríguez Rodríguez", "Valverde", "PRM"],
].map(([id, fullName, province, party]) => ({
  id,
  fullName,
  chamber: "senate" as const,
  province,
  representation: "provincial" as const,
  party,
  officialProfileUrl: "https://www.senadord.gob.do/",
  rosterSourceUrl: senateRosterSource,
  education: [],
  educationStatus: "pending" as const,
  educationNote: "Currículo educativo en verificación documental.",
  ...senatorEnrichment[id],
}));

export const deputies: Legislator[] = [];

export const legislators = [...senators, ...deputies];
