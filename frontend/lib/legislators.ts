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
      {
        level: "grado",
        credential: "Doctora en Medicina",
        institution: "Universidad Central del Este (UCE)",
        status: "completed",
        sourceUrl: "https://www.senadord.gob.do/provincia/azua/",
      },
      {
        level: "especialidad",
        credential: "Médico Pediatra",
        institution: "Hospital Materno Infantil San Lorenzo de Los Mina / UASD",
        status: "completed",
        sourceUrl: "https://www.senadord.gob.do/provincia/azua/",
      },
      {
        level: "formación continua",
        credential: "Infectología Pediátrica; manejo y tratamiento del dengue",
        institution: "San Juan, Puerto Rico",
        status: "completed",
        sourceUrl: "https://www.senadord.gob.do/provincia/azua/",
      },
    ],
  },
  "omar-leonel-fernandez-dominguez": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/distrito-nacional/",
    educationStatus: "verified",
    education: [
      {
        level: "grado",
        credential: "Licenciatura en Derecho",
        institution: "Pontificia Universidad Católica Madre y Maestra (PUCMM)",
        status: "completed",
        sourceUrl: "https://www.senadord.gob.do/provincia/distrito-nacional/",
      },
      {
        level: "maestría",
        credential: "Máster en Derecho de los Negocios Internacionales",
        institution: "Boston University",
        status: "completed",
        sourceUrl: "https://www.senadord.gob.do/provincia/distrito-nacional/",
      },
    ],
  },
  "franklin-martin-romero-morillo": {
    officialProfileUrl: "https://www.senadord.gob.do/provincia/duarte/",
    educationStatus: "verified",
    education: [
      {
        level: "secundaria/equivalencia",
        credential: "GED",
        institution: "Estados Unidos",
        status: "completed",
        sourceUrl: "https://www.senadord.gob.do/provincia/duarte/",
      },
      {
        level: "grado",
        credential: "Derecho",
        status: "completed",
        sourceUrl: "https://www.senadord.gob.do/provincia/duarte/",
      },
      {
        level: "maestría",
        credential: "Derecho Constitucional y Derecho Público",
        institution: "Universidad de Castilla-La Mancha",
        status: "in_progress",
        sourceUrl: "https://www.senadord.gob.do/provincia/duarte/",
      },
      {
        level: "maestría",
        credential: "Gestión Pública y Liderazgo, especialidad en Derecho Administrativo",
        institution: "Universidad Europea del Atlántico (UNEATLANTICO)",
        status: "in_progress",
        sourceUrl: "https://www.senadord.gob.do/provincia/duarte/",
      },
    ],
  },
  "ricardo-de-los-santos-polanco": {
    officialProfileUrl:
      "https://memoriahistorica.senadord.gob.do/items/8a4bd1e3-2a5c-4061-b3e4-989bf29bdc5f/full",
    photoUrl:
      "https://memoriahistorica.senadord.gob.do/bitstreams/6738e97e-6424-474b-95e1-46d7fd13cd53/download",
    educationStatus: "verified",
    education: [
      {
        level: "grado",
        credential: "Licenciatura en Administración de Empresas",
        institution: "Universidad de la Tercera Edad (UTE)",
        status: "completed",
        sourceUrl:
          "https://memoriahistorica.senadord.gob.do/items/8a4bd1e3-2a5c-4061-b3e4-989bf29bdc5f/full",
      },
      {
        level: "maestría",
        credential: "Comunicación Corporativa",
        institution: "TECH Universidad Tecnológica",
        status: "completed",
        sourceUrl:
          "https://memoriahistorica.senadord.gob.do/items/8a4bd1e3-2a5c-4061-b3e4-989bf29bdc5f/full",
      },
      {
        level: "maestría",
        credential:
          "Derecho Constitucional y Derecho Público: Derechos Fundamentales y Derechos Constitucionales",
        institution: "Universidad de Castilla-La Mancha",
        status: "in_progress",
        sourceUrl:
          "https://memoriahistorica.senadord.gob.do/items/8a4bd1e3-2a5c-4061-b3e4-989bf29bdc5f/full",
      },
    ],
  },
};

// Canonical 2024-2028 Senate roster. Names/provinces are grounded in the
// official Senate certificate-delivery roster. Current party labels follow
// the Senate's current party representation page where available.
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
